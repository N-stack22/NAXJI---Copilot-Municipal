WITH autorizados AS MATERIALIZED (
    SELECT f.*, d.titulo, d.procedencia, d.sha256, d.tipo, d.nombre_original
    FROM public.documento_fragmentos f
    JOIN public.documentos d ON d.id = f.documento_id
    WHERE (%s OR d.usuario_id = %s OR d.ambito = 'INSTITUCIONAL'
           OR (d.ambito = 'AREA' AND d.area_id = %s))
      AND d.estado = 'INDEXADO'
      AND d.procesamiento = %s
      AND f.procesamiento = d.procesamiento
)
SELECT *, 1 - (embedding <=> %s::vector) AS similitud
FROM autorizados
WHERE 1 - (embedding <=> %s::vector) >= %s
ORDER BY embedding <=> %s::vector, id
LIMIT %s
