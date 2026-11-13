UPDATE public.documentos SET estado=%s,intento=%s,reserva_hasta=%s,error=NULL,
                         updated_at=now() WHERE id=%s
