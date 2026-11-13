SELECT m.*, to_jsonb(n) AS documento
                FROM public.normativa_correspondencias m
                JOIN public.normativas n ON n.id=m.normativa_id
                WHERE m.etiqueta=ANY(%s) ORDER BY m.etiqueta,n.codigo,n.id
