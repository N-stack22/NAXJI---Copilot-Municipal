DELETE FROM public.solicitud_valores WHERE solicitud_id=%s AND NOT (id=ANY(%s::uuid[]))
