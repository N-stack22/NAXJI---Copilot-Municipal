-- Corrección de la función existente; no crea procedimientos duplicados.
-- Revisar antes de aplicar en una base real. Si hay títulos inválidos, revierte
-- toda la migración: no corrige ni reescribe documentos del usuario.
BEGIN;
SET LOCAL lock_timeout = '5s';
SELECT pg_advisory_xact_lock(20260930, 1);

CREATE OR REPLACE FUNCTION public.naxji_secciones_salida_validas(valor jsonb)
RETURNS boolean LANGUAGE plpgsql IMMUTABLE SET search_path = pg_catalog AS $$
DECLARE
  seccion jsonb;
  claves text[] := ARRAY[]::text[];
  clave text;
  -- Caracteres Unicode que Python considera blancos (str.strip()). btrim()
  -- sin segundo argumento solo elimina U+0020; POSIX depende del locale.
  espacios constant text := U&'\0009\000A\000B\000C\000D\001C\001D\001E\001F\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000';
BEGIN
  IF valor IS NULL THEN RETURN true; END IF;
  IF jsonb_typeof(valor) <> 'array' THEN RETURN false; END IF;
  IF jsonb_array_length(valor) NOT BETWEEN 1 AND 100 THEN RETURN false; END IF;
  FOR seccion IN SELECT * FROM jsonb_array_elements(valor) LOOP
    IF jsonb_typeof(seccion) <> 'object' THEN RETURN false; END IF;
    IF NOT (seccion ?& ARRAY['clave','titulo','obligatoria'])
       OR (seccion - ARRAY['clave','titulo','obligatoria']) <> '{}'::jsonb THEN RETURN false; END IF;
    IF jsonb_typeof(seccion->'clave') <> 'string'
       OR jsonb_typeof(seccion->'titulo') <> 'string'
       OR jsonb_typeof(seccion->'obligatoria') <> 'boolean' THEN RETURN false; END IF;
    clave := seccion->>'clave';
    IF clave !~ '^[a-z][a-z0-9_]{0,79}$'
       OR clave = ANY(ARRAY['encabezado','datos','contexto','plantilla','instrucciones'])
       OR clave = ANY(claves)
       OR length(btrim(seccion->>'titulo', espacios)) = 0
       OR length(seccion->>'titulo') > 150 THEN RETURN false; END IF;
    claves := array_append(claves, clave);
  END LOOP;
  RETURN true;
END $$;

-- Cambiar una función IMMUTABLE no revalida filas existentes. Recrear las
-- restricciones fuerza su comprobación y el rollback si alguna fila no cumple.
ALTER TABLE public.plantillas DROP CONSTRAINT IF EXISTS chk_plantilla_secciones_salida;
ALTER TABLE public.plantillas ADD CONSTRAINT chk_plantilla_secciones_salida
  CHECK (public.naxji_secciones_salida_validas(secciones_salida)) NOT VALID;
ALTER TABLE public.versiones_informe DROP CONSTRAINT IF EXISTS chk_version_secciones_salida;
ALTER TABLE public.versiones_informe ADD CONSTRAINT chk_version_secciones_salida
  CHECK (public.naxji_secciones_salida_validas(secciones_salida)) NOT VALID;
ALTER TABLE public.plantillas VALIDATE CONSTRAINT chk_plantilla_secciones_salida;
ALTER TABLE public.versiones_informe VALIDATE CONSTRAINT chk_version_secciones_salida;
COMMIT;
