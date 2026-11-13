SELECT count(*) AS n FROM public.documentos d WHERE (%s OR d.usuario_id=%s OR d.ambito='INSTITUCIONAL'
                   OR (d.ambito='AREA' AND d.area_id=%s)) AND d.estado='INDEXADO' AND d.procesamiento=%s
