-- Aplicación manual exclusivamente en entorno autorizado. No modifica registros anteriores.
BEGIN;
CREATE TABLE IF NOT EXISTS public.revision_eventos (
    secuencia bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id uuid NOT NULL UNIQUE,
    informe_id uuid NOT NULL REFERENCES public.informes(id),
    version_id uuid NOT NULL REFERENCES public.versiones_informe(id),
    usuario_id uuid,
    accion text NOT NULL CHECK (accion IN ('CREAR_VERSION','ENVIAR_REVISION','EDITAR_REVISION','APROBADO','RECHAZADO','EXPORTAR')),
    estado text NOT NULL CHECK (estado IN ('BORRADOR','EN_REVISION','APROBADO','RECHAZADO')),
    fecha timestamptz NOT NULL DEFAULT now(),
    detalle jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS revision_eventos_informe ON public.revision_eventos(informe_id, secuencia);
CREATE OR REPLACE FUNCTION public.revision_eventos_inmutable() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Los eventos de revision son inmutables'; END $$;
DROP TRIGGER IF EXISTS revision_eventos_inmutable ON public.revision_eventos;
CREATE TRIGGER revision_eventos_inmutable BEFORE UPDATE OR DELETE ON public.revision_eventos
FOR EACH ROW EXECUTE FUNCTION public.revision_eventos_inmutable();
ALTER TABLE public.revision_eventos ENABLE ROW LEVEL SECURITY;
-- Sin políticas públicas: acceso únicamente mediante el backend con su rol privado.
REVOKE ALL ON public.revision_eventos FROM PUBLIC;
COMMIT;
