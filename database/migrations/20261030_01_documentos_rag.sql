-- Revisar y aplicar explícitamente en una base aislada primero. Sin semillas.
BEGIN;
SET LOCAL lock_timeout='5s';
SELECT pg_advisory_xact_lock(20261030,1);
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;
-- En Supabase vector puede existir en extensions; conservar su instalación.
SET LOCAL search_path=public,extensions,pg_catalog;
CREATE TABLE IF NOT EXISTS public.documentos (
 id uuid PRIMARY KEY,
 titulo text NOT NULL CHECK(length(btrim(titulo)) BETWEEN 1 AND 250),
 nombre_original text NOT NULL,
 tipo text NOT NULL CHECK(tipo IN ('pdf','docx','txt')),
 tamano bigint NOT NULL CHECK(tamano>0),
 sha256 text NOT NULL CHECK(sha256 ~ '^[a-f0-9]{64}$'),
 usuario_id uuid NOT NULL REFERENCES public.perfiles(id),
 procedencia text NOT NULL CHECK(length(btrim(procedencia)) BETWEEN 1 AND 1000),
 ambito text NOT NULL CHECK(ambito IN ('PRIVADO','AREA','INSTITUCIONAL')),
 area_id uuid REFERENCES public.areas_municipales(id),
 ubicacion text NOT NULL UNIQUE,
 estado text NOT NULL CHECK(estado IN ('SUBIENDO','ERROR_CARGA','CARGADO','PROCESANDO','ERROR_PROCESAMIENTO','INDEXADO')),
 error text,
 intento uuid,
 reserva_hasta timestamptz,
 procesamiento text,
 fragmentos integer NOT NULL DEFAULT 0 CHECK(fragmentos>=0),
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK ((ambito='AREA') = (area_id IS NOT NULL)),
 CHECK ((intento IS NULL) = (reserva_hasta IS NULL)),
 CHECK (estado <> 'INDEXADO' OR (procesamiento IS NOT NULL AND fragmentos>0))
);
CREATE UNIQUE INDEX IF NOT EXISTS documentos_deduplicacion
 ON public.documentos(usuario_id,ambito,COALESCE(area_id,'00000000-0000-0000-0000-000000000000'::uuid),sha256);
CREATE TABLE IF NOT EXISTS public.documento_fragmentos (
 id uuid PRIMARY KEY,
 documento_id uuid NOT NULL REFERENCES public.documentos(id) ON DELETE CASCADE,
 orden integer NOT NULL CHECK(orden>=0),
 texto text NOT NULL CHECK(length(texto)>0),
 localizacion text NOT NULL,
 inicio integer NOT NULL CHECK(inicio>=0),
 fin integer NOT NULL CHECK(fin>inicio),
 embedding vector(1024) NOT NULL,
 procesamiento text NOT NULL,
 UNIQUE(documento_id,orden)
);
-- El PMV2 usa búsqueda exacta sobre corpus autorizado; no ANN con filtrado tardío.
ALTER TABLE public.versiones_informe ADD COLUMN IF NOT EXISTS sustento jsonb;
CREATE TABLE IF NOT EXISTS public.version_citas (
 version_id uuid NOT NULL REFERENCES public.versiones_informe(id),
 documento_id uuid NOT NULL REFERENCES public.documentos(id),
 -- Sin FK al índice mutable: el snapshot sobrevive a una reindexación.
 fragmento_id uuid NOT NULL,
 seccion text NOT NULL,
 pasaje text NOT NULL,
 estado text NOT NULL CHECK(estado IN ('PENDIENTE_REVISION','TEXTO_MODIFICADO')),
 snapshot jsonb NOT NULL,
 PRIMARY KEY(version_id,fragmento_id,seccion)
);
ALTER TABLE public.documentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documento_fragmentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.version_citas ENABLE ROW LEVEL SECURITY;
-- Tablas exclusivamente por API autenticada. No exponer ubicación ni snapshots
-- mediante Data API; el backend usa su rol existente y aplica usuario/área/roles.
REVOKE ALL ON public.documentos,public.documento_fragmentos,public.version_citas FROM PUBLIC;
DO $$ DECLARE rol text; BEGIN
 FOREACH rol IN ARRAY ARRAY['anon','authenticated'] LOOP
  IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=rol) THEN
   EXECUTE format('REVOKE ALL ON public.documentos,public.documento_fragmentos,public.version_citas FROM %I',rol);
   -- sustento se devuelve SOLO por FastAPI; la política PMV1 de versiones permite
   -- lectura al dueño del informe pero no comprueba el acceso actual a cada fuente.
   EXECUTE format('REVOKE SELECT ON public.versiones_informe FROM %I',rol);
  END IF;
 END LOOP;
END $$;
COMMIT;
