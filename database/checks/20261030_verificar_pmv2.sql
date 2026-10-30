-- Solo lectura: cero filas en las tres primeras consultas significa integridad.
SELECT d.id,d.fragmentos,count(f.id) FROM public.documentos d
LEFT JOIN public.documento_fragmentos f ON f.documento_id=d.id
WHERE d.estado='INDEXADO' GROUP BY d.id HAVING d.fragmentos<>count(f.id);
SELECT f.id FROM public.documento_fragmentos f JOIN public.documentos d ON d.id=f.documento_id
WHERE d.estado='INDEXADO' AND d.procesamiento<>f.procesamiento;
SELECT c.version_id FROM public.version_citas c JOIN public.versiones_informe v ON v.id=c.version_id
WHERE v.sustento IS NULL;
SELECT relname,relrowsecurity FROM pg_class WHERE oid IN
('public.documentos'::regclass,'public.documento_fragmentos'::regclass,'public.version_citas'::regclass);
SELECT extname,extversion FROM pg_extension WHERE extname='vector';
