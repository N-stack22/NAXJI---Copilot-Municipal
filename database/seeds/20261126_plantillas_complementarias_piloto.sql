-- Opcional, aditivo e idempotente. Tipos del catálogo existente; estructuras piloto.
-- No acredita aprobación de formatos institucionales ni añade clases al modelo ML.
BEGIN;
SELECT pg_advisory_xact_lock(20261126, 1);
INSERT INTO public.plantillas(nombre,tipo_informe_id,version,descripcion,secciones_salida)
SELECT v.nombre,t.id,1,
 'PILOTO NAXJI. Estructura genérica para revisión humana; no es un formato institucional aprobado.',
 '[{"clave":"antecedentes","titulo":"Antecedentes","obligatoria":true},{"clave":"desarrollo","titulo":"Desarrollo","obligatoria":true},{"clave":"conclusiones","titulo":"Conclusiones","obligatoria":true}]'::jsonb
FROM (VALUES ('INFORME_LEGAL','Informe Legal – Piloto NAXJI'),('MEMORANDO','Memorando – Piloto NAXJI')) AS v(codigo,nombre)
JOIN public.tipos_informe t ON t.codigo=v.codigo AND t.activo
ON CONFLICT(nombre,version) DO NOTHING;
INSERT INTO public.campos_plantilla(plantilla_id,clave,etiqueta,tipo_dato,obligatorio,orden,configuracion)
SELECT p.id,v.clave,v.etiqueta,'textarea',true,v.orden,'{}'::jsonb
FROM (VALUES ('antecedentes','Antecedentes comprobables',1),('detalle','Contenido y datos fuente',2),('conclusiones','Conclusiones propuestas',3)) AS v(clave,etiqueta,orden)
JOIN public.plantillas p ON p.nombre IN ('Informe Legal – Piloto NAXJI','Memorando – Piloto NAXJI') AND p.version=1
ON CONFLICT(plantilla_id,clave) DO NOTHING;
COMMIT;
