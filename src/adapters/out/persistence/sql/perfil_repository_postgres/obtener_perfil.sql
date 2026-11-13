SELECT p.*, a.nombre AS area_nombre FROM public.perfiles p LEFT JOIN public.areas_municipales a ON a.id=p.area_id WHERE p.id=%s
