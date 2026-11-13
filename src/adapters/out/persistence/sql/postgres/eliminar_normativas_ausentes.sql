DELETE FROM public.prediccion_normativas WHERE prediccion_id=%s AND NOT (id=ANY(%s::uuid[]))
