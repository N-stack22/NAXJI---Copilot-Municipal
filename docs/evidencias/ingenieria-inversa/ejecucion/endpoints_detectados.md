# Prompt 6 — Operaciones HTTP contrastadas con código

Main **4f4d294**, corte 27/11/2026. [Inventario estático actualizado](../cierre-documental-20261127/rutas-estaticas.json):**42 operaciones visibles** derivadas de decoradores de controladores y`app.add_api_route`, más el alias POST `/solicitudes/` con `include_in_schema=False`. Es lecturaAST, no una nueva ejecución de OpenAPI ni consulta productiva. Coincide con el [inventarioOpenAPI histórico](../../cierre-trazable/ingenieria-inversa/inventario.json).

| Familia | Fuente y operaciones observadas |
| ---| ---|
| Sesión/perfil | [auth_controller](../../../../src/adapters/in/controllers/auth_controller.py), [usuario_controller](../../../../src/adapters/in/controllers/usuario_controller.py): config, login, refresh, logout,`/auth/me`. |
| Catálogos/solicitudes | [catalogo_controller](../../../../src/adapters/in/controllers/catalogo_controller.py), [solicitud_controller](../../../../src/adapters/in/controllers/solicitud_controller.py): tipos, áreas, plantillas, campos, solicitud, formulario completo, valores, informe asociado. |
| Contexto/generación | [ia_controller](../../../../src/adapters/in/controllers/ia_controller.py): contexto, predecir, validar, generar. |
| Informe legacy | [informe_controller](../../../../src/adapters/in/controllers/informe_controller.py): leer, versión, editarBORRADOR yDOCX con permisos de lectura. No se afirma que esta exportación histórica exija aprobaciónPMV 3. |
| Documentos | [documento_controller](../../../../src/adapters/in/controllers/documento_controller.py): configuración, listar, cargar, recuperar, obtener, procesar, fragmento, original; bandera y permisos del servidor. |
| PMV 3 | [revision_controller](../../../../src/adapters/in/controllers/revision_controller.py): config, lista, historial, enviar, editar, decidir, exportar versión a probada y`/auditoria`. |
| Diagnóstico | [main.health](../../../../src/main.py), [operacion_controller](../../../../src/adapters/in/controllers/operacion_controller.py):`/health` público; liveness;`/ready` privado para administración. |

El listado no acredita disponibilidad remota ni sustituye los permisos de aplicación. Los nombres, verbos, rutas, archivo y línea exactos están en el JSON. [Reglas de acceso y estados](../analisis/dominio.md), [42 operaciones históricas](../../cierre-trazable/ingenieria-inversa/inventario.json).

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Endpoints detectados

Inventario generado desde OpenAPI local en `../../cierre-trazable/ingenieria-inversa/inventario.json`: 42 operaciones documentadas. Incluye catálogos, solicitudes, contexto/predicción/confirmación, generación, informes/versiones, originales/fragmentos/recuperación, Auth, revisión/auditoría y diagnóstico.

PMV3: GET `/revision/config`, GET `/revision/informes`, GET `/revision/informes/{id}`, POST `.../enviar`, `.../editar`, `.../decidir`, GET `.../versiones/{n}/exportar` y GET `/auditoria`. Exportar requiere versión aprobada; solo administración consulta auditoría. GET `/ready` requiere administrador. La documentación pública es desactivable; no se consultó el OpenAPI productivo como evidencia de esta reconstrucción.
