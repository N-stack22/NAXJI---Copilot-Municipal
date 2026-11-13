UPDATE public.documentos SET estado=%s,error=%s,reserva_hasta=NULL,intento=NULL,
                fragmentos=CASE WHEN %s THEN %s ELSE fragmentos END,
                procesamiento=COALESCE(%s,procesamiento),updated_at=now() WHERE id=%s
