# Endpoints detectados

Inventario generado desde OpenAPI local en `../../cierre-trazable/ingenieria-inversa/inventario.json`: 42 operaciones documentadas. Incluye catálogos, solicitudes, contexto/predicción/confirmación, generación, informes/versiones, originales/fragmentos/recuperación, Auth, revisión/auditoría y diagnóstico.

PMV3: GET `/revision/config`, GET `/revision/informes`, GET `/revision/informes/{id}`, POST `.../enviar`, `.../editar`, `.../decidir`, GET `.../versiones/{n}/exportar` y GET `/auditoria`. Exportar requiere versión aprobada; solo administración consulta auditoría. GET `/ready` requiere administrador. La documentación pública es desactivable; no se consultó el OpenAPI productivo como evidencia de esta reconstrucción.
