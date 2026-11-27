SELECT i.id, i.titulo, i.estado, i.creado_por, i.created_at AS fecha
FROM informes i JOIN solicitudes s ON s.id = i.solicitud_id
WHERE (%s OR s.usuario_id = %s OR (%s AND s.area_destino_id = %s))
ORDER BY i.created_at DESC, i.id DESC LIMIT %s OFFSET %s
