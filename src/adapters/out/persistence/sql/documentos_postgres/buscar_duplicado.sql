SELECT * FROM public.documentos WHERE usuario_id=%s AND ambito=%s
                            AND area_id IS NOT DISTINCT FROM %s AND sha256=%s
