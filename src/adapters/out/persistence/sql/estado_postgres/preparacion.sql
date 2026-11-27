SELECT to_regclass('public.documentos') IS NOT NULL,
       to_regclass('public.revision_eventos') IS NOT NULL,
       EXISTS (SELECT 1 FROM pg_extension WHERE extname='vector')
