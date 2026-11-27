SELECT id, informe_id, version_id, usuario_id, accion, estado, fecha, detalle
FROM revision_eventos WHERE informe_id = %s ORDER BY secuencia
