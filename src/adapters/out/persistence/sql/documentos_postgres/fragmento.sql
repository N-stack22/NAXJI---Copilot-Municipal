SELECT id,documento_id,texto,localizacion,inicio,fin,procesamiento
                FROM public.documento_fragmentos WHERE id=%s AND documento_id=%s
