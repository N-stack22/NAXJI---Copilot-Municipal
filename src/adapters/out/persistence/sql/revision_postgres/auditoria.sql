SELECT id, informe_id, version_id, usuario_id, accion, estado, fecha, detalle
FROM revision_eventos WHERE (%s::uuid IS NULL OR informe_id = %s)
ORDER BY secuencia DESC LIMIT %s OFFSET %s
