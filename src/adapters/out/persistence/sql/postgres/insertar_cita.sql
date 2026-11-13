INSERT INTO public.version_citas
                                    (version_id,documento_id,fragmento_id,seccion,pasaje,estado,snapshot)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
