SELECT d.* FROM public.documentos d WHERE (%s OR d.usuario_id=%s OR d.ambito='INSTITUCIONAL'
                   OR (d.ambito='AREA' AND d.area_id=%s)) ORDER BY d.created_at DESC,d.id LIMIT %s OFFSET %s
