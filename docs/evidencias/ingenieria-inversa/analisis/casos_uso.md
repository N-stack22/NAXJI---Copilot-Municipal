# Prompt 7 — Descubrimiento funcional de los tres PMV

Main **4f4d294**, corte 27/11/2026. Los tres PMV y las diez HU se consideran completos **dentro del alcance académico acordado**. Las validaciones institucionales quedan fuera; los 12 prompts son análisis, no historias adicionales.

| PMV | HU original | Implementación verificable | Evidencia existente |
| ---| ---| ---| ---|
| 1| HU-001 Acceso/perfil| [Auth](../../../../src/infrastructure/auth/supabase.py), [controladores](../../../../src/adapters/in/controllers/auth_controller.py), [sesiónWeb](../../../../src/adapters/in/web/services/session.js)| [tests_auth](../../../../tests/test_auth.py), [matriz HU](../../../matriz_trazabilidad.md)|
| 1| HU-002 Configurar solicitud/formulario| [CrearSolicitud](../../../../src/application/use_cases/crear_solicitud.py), [GuardarSolicitudCompleta](../../../../src/application/use_cases/guardar_solicitud_completa.py), [ConsultarCatalogos](../../../../src/application/use_cases/consultar_catalogos.py)| [pruebasPMV 1](../../../../tests/test_cierre_pmv1.py)|
| 1| HU-IA-01 Sugerir/confirmar contexto y generar| [PredecirContexto](../../../../src/application/use_cases/predecir_contexto.py), [ValidarPrediccion](../../../../src/application/use_cases/validar_prediccion.py), [GenerarBorrador](../../../../src/application/use_cases/generar_borrador.py)| [matriz HU](../../../matriz_trazabilidad.md), [O llama real histórico](../../cierre-trazable/ollama-real/)|
| 2| HU-003 Cargar/procesar fuentes| [GestionDocumentos](../../../../src/application/use_cases/documentos.py)| [test_pmv 2](../../../../tests/test_pmv2.py), [PG/pgvector](../../../../tests/test_pmv2_postgres.py)|
| 2| HU-IA-02 Recuperar con permisos|`GestionDocumentos.recuperar`, [buscar.sql](../../../../src/adapters/out/persistence/sql/documentos_postgres/buscar.sql)| [RAG real](../../cierre-trazable/rag-embeddings-reales.json)|
| 2| HU-IA-03 Citas y fuentes|`vincular_citas`, `GestionDocumentos.proteger`, [ObtenerInforme](../../../../src/application/use_cases/obtener_informe.py)| [tests PMV 2](../../../../tests/test_pmv2.py), [capturas](../../capturas-hu-20261126/README.md)|
| 3| HU-IA-04 Señalar respaldo insuficiente| [respaldo.py](../../../../src/domain/services/respaldo.py), [RevisionInformes](../../../../src/application/use_cases/revision_informes.py)| [test_pmv 3](../../../../tests/test_pmv3.py); avisos intactos|
| 3| HU-004 Editar, a probar o rechazar|`RevisionInformes.enviar/editar/decidir`| [test_pmv 3_postgres](../../../../tests/test_pmv3_postgres.py)|
| 3| HU-005 Versiones y exportación|`RevisionInformes.historial/exportar`, [exportadores](../../../../src/adapters/out/documents/)| [test_pmv 3](../../../../tests/test_pmv3.py)|
| 3| HU-006 Auditoría|`RevisionInformes.auditoria`, [RevisionRepository](../../../../src/application/ports/output/revision_repository.py)| [test_pmv 3](../../../../tests/test_pmv3.py), [capturas](../../capturas-hu-20261126/README.md)|

Los casos deuso complementarios de obtener, actualizar solicitud/valores, borrador, contexto y exportación legacy están inventariados en [dominio, PMV y contratos](dominio.md). La revisión implementada es de una etapa por revisor del destino distinto del autor; APROBADOR heredado no crea una segunda etapa. No se añaden móvil, imágenes OCR universal ni requerimientos a partir de patrones ausentes.

Resultados conservados:375 backend a probadas/21 omitidas, 55 frontend; 750 respuestas esperadas, 0 fallos inesperados. [Resultados y límites](../../../RESULTADOS_CIERRE.md); no se suman las corridas ni se contabilizan omitidas como a probadas.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Casos de uso observados

HU-001: acceso/sesión/perfil; HU-002: configurar tipo/área/plantilla/datos; HU-IA-01: sugerir/confirmar contexto y generar. HU-003: incorporar/procesar fuentes; HU-IA-02: recuperar con permisos; HU-IA-03: mostrar citas/snapshots. HU-IA-04: advertir y revisar respaldo; HU-004: editar/decidir; HU-005: historial y exportación aprobada; HU-006: auditoría administrativa.

Son las diez HU originales, no doce funcionalidades nuevas inferidas de los prompts de auditoría. `matriz_trazabilidad.md` enlaza criterios, archivos, pruebas y límites. Móvil/imágenes no forman parte del producto. El rol APROBADOR heredado no introduce una segunda etapa de aprobación.
