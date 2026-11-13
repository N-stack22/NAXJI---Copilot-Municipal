INSERT INTO public.documento_fragmentos
                        (id,documento_id,orden,texto,localizacion,inicio,fin,embedding,procesamiento)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s::vector,%s)
