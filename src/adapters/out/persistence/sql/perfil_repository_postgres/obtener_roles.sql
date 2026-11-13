SELECT r.codigo FROM public.usuario_roles ur JOIN public.roles r ON r.id=ur.rol_id WHERE ur.usuario_id=%s AND r.activo
