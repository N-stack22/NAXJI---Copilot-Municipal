# Evaluación formativa de arquitectura, API, predicción y SQL

Fecha: 2026-10-23. Repositorio: `N-stack22/NAXJI---Copilot-Municipal`.
Base: `b4c0f82301aae3bd21c494ad9bd4809beaff45dd`.
Rama de revisión: `audit/criterios-hexagonal-api-prediccion-sql`.

Esta evaluación usa los cinco enunciados proporcionados, no una rúbrica detallada
del profesor ni un umbral de precisión supuesto. «Cumple» significa que los
requisitos observables descritos aquí se verificaron; no certifica los servicios
externos ni requisitos académicos adicionales no especificados.

La revisión final parte de `946738ba1dbf5cfc90b0140aaaacaa499ad54949`.
Los apartados A–F al final de este documento contienen el dictamen vigente y las
evidencias nuevas. Las secciones anteriores se conservan como historial de las
cuatro correcciones originales, verificadas de nuevo y sin repetirlas.

## Resultados de la primera auditoría (histórico)

Las rutas de la tabla son relativas a `/workspace/NAXJI---Copilot-Municipal`.
Las líneas corresponden al código final, salvo las referencias marcadas «base».

| Criterio | Resultado inicial | Hallazgo y evidencia | Acción implementada | Archivos modificados | Pruebas | Estado final |
|---|---|---|---|---|---|---|
| 1. Carpetas con arquitectura hexagonal | Cumple | Existen dominio, aplicación con puertos y casos de uso, adaptadores de entrada/salida e infraestructura. `tests/test_arquitectura.py:6` comprueba aislamiento. No se encontró necesidad de mover carpetas. | Conservar estructura; documentar inspección y límites. | `docs/AUDITORIA_FORMATIVA.md` | Pruebas de arquitectura e importación aprobadas; inspección AST sin dependencias prohibidas. | Cumple en la estructura observada. |
| 2. Responsabilidades de cada capa | Parcial | `src/application/use_cases/servicios_solicitud.py:62`: la validación de tipos activos ocurría antes de inferir el tipo desde la plantilla; esa inferencia eludía la regla. | Comprobar que el tipo inferido exista y esté activo dentro de la aplicación, sin trasladar la regla al controlador o al adaptador SQL. | `src/application/use_cases/servicios_solicitud.py`; `tests/test_auditoria_criterios.py`; este informe. | Cuatro casos REST: crear/actualizar con tipo inactivo/ausente, sin escritura parcial; caso válido conservado. | Cumple las responsabilidades y reglas verificadas. |
| 3. Integración Python mediante API REST | Parcial | `src/domain/services/solicitud_service.py:34`: `math.isfinite(10**400)` lanzaba `OverflowError`, propagando un error interno al guardar un número JSON válido. | Validar los enteros como finitos sin conversión a float; mantener rechazo de booleanos y floats no finitos. | `src/domain/services/solicitud_service.py`; `tests/test_auditoria_criterios.py`; este informe. | Guardar y recuperar el entero exacto por HTTP; regresiones de tipos inválidos, contratos, permisos, versiones y exportación aprobadas. | Cumple en integración local automatizada; Supabase/Ollama reales no verificados. |
| 4. Precisión y resultados predictivos | Parcial, rendimiento no demostrado | `src/adapters/out/ai/sklearn_context_predictor.py:297` (base) identificaba las predicciones como `SKLEARN_RF_IA_01`, pero los estimadores cargados son regresiones logísticas. No hay corpus etiquetado independiente ni umbral de aceptación. El clasificador de tipo tiene tres clases; el catálogo también contiene `MEMORANDO`, ausente del artefacto. | Identificar nuevas predicciones como `SKLEARN_IA_01`; obtener y persistir nombres de los estimadores reales y exponerlos en REST; explicar confianza frente a precisión. Conservar versión histórica y artefactos, sin reentrenar con datos inventados. | `src/adapters/out/ai/sklearn_context_predictor.py`; `src/adapters/in/schemas/prediccion_response.py`; `src/main.py`; `README.md`; `tests/test_postgres.py`; `tests/test_correspondencias_postgres.py`; `tests/test_auditoria_criterios.py`; este informe. | Inferencia real y metadatos por HTTP aprobados; integración de catálogos aprobada. No se calculó accuracy/precision/recall/F1 sin referencias independientes. | Parcial: trazabilidad corregida; precisión y cobertura completa pendientes de datos y criterios de aceptación. |
| 5. Procedimientos almacenados | Parcial | Se encontraron cinco funciones almacenadas, incluidos dos triggers; no hay `CREATE PROCEDURE`/`CALL`. La función `database/migrations/20260930_01_secciones_salida.sql:27` acepta títulos de solo tabulaciones, saltos de línea o U+00A0 que el dominio rechaza. | Corregir la función existente mediante migración posterior; alinear blancos Unicode, recrear y validar restricciones en una transacción. No crear rutinas de negocio duplicadas sin requisito específico. | `database/migrations/20261023_01_validar_titulos_secciones.sql`; `tests/test_auditoria_criterios.py`; este informe. | PostgreSQL 16 desechable: idempotencia, rechazo en ambas tablas, conservación de filas y rollback ante datos anteriores inválidos. Funciones Auth/RLS existentes probadas con dobles locales. | Funciones verificadas localmente; parcial si el profesor exige procedimientos `CREATE PROCEDURE` concretos. No se validó ni migró Supabase real. |

## Hallazgos reproducidos y alcance de las correcciones

### Referencias inferidas

Antes del cambio, crear una solicitud omitiendo `tipo_informe_id` pero indicando
una plantilla cuyo tipo estaba inactivo guardaba el tipo inactivo. La comprobación
previa solo examinaba el valor inicial, que era `None`. Ahora la inferencia tiene
la misma restricción que la selección explícita. Una actualización fallida conserva
la solicitud original por rollback. No cambian las plantillas válidas del PMV1.

### Números en el dominio y REST

Un entero de 401 dígitos es finito y aceptable como JSON; `math.isfinite` intentaba
convertirlo a float y fallaba. La corrección evita esa conversión y mantiene los
tipos booleanos separados de los enteros. La prueba reproduce el guardado y la
recuperación por REST, sin pérdida de dígitos. No se afirma que JavaScript represente
exactamente tales números como `Number`; la corrección corresponde al contrato Python.

### Identificación y evaluación del predictor

La inspección de los cinco artefactos `.joblib` y `model_config.json` comprobó:

| Salida | Artefacto / estimador real | Cobertura observada |
|---|---|---|
| Tipo de informe | Pipeline con `LogisticRegression` | Informe Legal, Informe Técnico e Informe de Inspección. No incluye Memorando. |
| Área | Pipeline con `LogisticRegression` | Seis clases de la PoC. Las correspondencias institucionales siguen sujetas a confirmación. |
| Temas normativos | `FeatureUnion` + `OneVsRestClassifier` con `LogisticRegression`; `MultiLabelBinarizer` | Once etiquetas temáticas. No equivalen a once normas jurídicas verificadas. |

No se modificaron pesos, vocabularios, umbral `0.25`, orden de resultados, cálculo
de probabilidades ni clases. `RF-IA-01-200CASOS-v1` se mantiene como identificador
histórico del artefacto, sin afirmar que pruebe la existencia o independencia de
200 casos de evaluación. Las nuevas predicciones guardan `parametros.algoritmos`
y REST añade `algoritmos`; las antiguas devuelven `{}` si carecen del metadato.
El identificador `modelo` de las predicciones nuevas cambia a `SKLEARN_IA_01`;
no se reescriben registros históricos. Los consumidores que comparen literalmente
el identificador anterior deberán reconocer el nuevo. React usa `es_mock` y las
pruebas frontend conservaron el flujo.

La documentación y los JSON de evidencia contienen ejemplos y respuestas del
propio modelo, no un conjunto independiente con etiquetas verdaderas, procedencia
y separación respecto al entrenamiento. Usarlos como verdad de referencia falsearía
la evaluación. No se inventaron métricas ni se confundió `predict_proba` con precisión.
Para completar este criterio hacen falta casos representativos etiquetados por
especialistas, independencia del entrenamiento y umbrales acordados para tipo,
área y multietiqueta; también datos de Memorando si esa clase debe predecirse.

### Inventario de rutinas SQL existentes

| Rutina | Ubicación existente | Uso |
|---|---|---|
| `public.set_updated_at()` | `NAXJI_database_schema_actual.sql:19` | Trigger de timestamps de perfiles, plantillas, solicitudes, valores e informes. |
| `naxji_private.has_role(text[])` | `migrations/20260928_01_auth_rls.sql:10` | Verifica perfil activo y roles activos para RLS. |
| `naxji_private.can_read()` | `migrations/20260928_01_auth_rls.sql:26` | Autoriza lectura según roles del PMV1. |
| `naxji_private.create_pending_profile()` | `migrations/20260928_01_auth_rls.sql:107` | Trigger que crea perfiles pendientes e inactivos sin aceptar privilegios de metadata. |
| `public.naxji_secciones_salida_validas(jsonb)` | `database/migrations/20260930_01_secciones_salida.sql:7` | Valida estructuras ordenadas en plantillas y versiones. Corregida por migración nueva. |

Los bloques `DO` de semillas son anónimos; no se contaron como procedimientos
almacenados. Las funciones anteriores sí son rutinas almacenadas, pero no son
procedimientos PostgreSQL invocados con `CALL`. El enunciado no especifica qué
operaciones deberían implementarse como procedimientos. La ausencia literal de
`CREATE PROCEDURE` queda registrada, sin atribuirle una funcionalidad inventada.

La migración nueva requiere la migración de secciones original. El cambio de una
función `IMMUTABLE` no vuelve a comprobar automáticamente sus restricciones:
por eso la corrección las recrea y valida en ambas tablas dentro de una transacción.
Si hay títulos inválidos existentes, falla y revierte íntegramente, sin reescribir
datos del usuario. Requiere revisión y una ventana compatible con el bloqueo de
tablas antes de aplicarse en una base real. Solo se ejecutó en bases desechables.

## Validación y límites

Validación en el entorno ya preparado, sin cambiar `install_script` ni `start_skill`:

- Python, PostgreSQL local incluido: `NAXJI_TEST_PG_PORT=55433 .venv/bin/python -m pytest -q -ra`.
- Frontend: `npm run test:frontend`.
- Calidad y compilación: `npm run lint`, `npm run build`, `git diff --check`.
- Python: **246 aprobadas, 19 omitidas, 0 fallidas**, 30,16 s. Las diez regresiones
  de `tests/test_auditoria_criterios.py` están incluidas. Una advertencia de
  deprecación Starlette/httpx; no impide la ejecución.
- Frontend: **51 aprobadas, 0 omitidas, 0 fallidas**, 54,54 s.
- Lint, build Vite y `git diff --check`: aprobados.

PostgreSQL corre en un contenedor exclusivo con puerto enlazado solo a loopback,
usuario `naxji_step3` y bases de nombre aleatorio creadas y eliminadas por las
pruebas existentes. La simulación mínima de `auth.users`/`auth.uid()` permite probar
las funciones y políticas SQL, no certifica Supabase Auth. Se verificaron creación
inactiva sin roles automáticos, lectura según rol, aislamiento de perfiles y falta
de permiso directo para ejecutar el trigger de altas.

Las pruebas remotas de Supabase, sesiones reales y generación Ollama permanecen
optativas y no ejecutadas. No hubo conexiones ni cambios en Supabase real.
No se modificaron Trello, diseño visual, configuración del entorno ni artefactos
entrenados. Las cuatro correcciones quedaron guardadas y publicadas en `946738b`;
la revisión final se entrega en un commit adicional de la misma rama, sin fusionar.

## Alcance de inspección

Se examinaron las dependencias de los 123 archivos Python rastreados mediante AST,
incluidos los scripts auxiliares y las pruebas, sin infracciones detectadas de
dominio/aplicación hacia adaptadores, infraestructura o frameworks. También se
comprobó que dominio no depende de aplicación. Se revisaron los trece SQL rastreados
y se cargaron los cinco artefactos del predictor para inspeccionar sus estimadores
y clases. Las pruebas nuevas y la migración nueva se validaron adicionalmente.

La revisión funcional cubrió los puertos, casos de uso, entidades y reglas del
dominio; todos los controladores y esquemas REST; autenticación e inyección de
dependencias; adaptadores de memoria/PostgreSQL, predicción, generación y exportación;
y los servicios React que consumen esas rutas. Se contrastó con README, documentación
de contratos, catálogos, persistencia y evidencia predictiva. Las suites existentes
ejercitan el flujo PMV1, validaciones, autorización, concurrencia, rollback,
generación con dobles de Ollama, preservación de versiones y DOCX. El diseño visual
y archivos ajenos a los cinco criterios no se modificaron.

Ningún resultado de esta revisión permite inferir una precisión estadística a
partir de la cantidad de pruebas aprobadas. La cobertura de pruebas de software y
el rendimiento predictivo sobre datos independientes son evaluaciones distintas.

## A. Lista de cotejo final y evidencias

El estado inicial de esta revisión corresponde al commit corregido `946738b`,
no al estado anterior a las cuatro correcciones. El criterio REST se valora ahora
con el alcance externo explícito del nuevo encargo; su estado parcial no representa
una regresión del flujo local que ya funcionaba.

| N.º | Criterio | Estado inicial | Estado final | Evidencia |
|---|---|---|---|---|
| 1 | Estructura de arquitectura hexagonal | Cumple | Cumple | Árbol real y mapa de capas; pruebas de arquitectura aprobadas. |
| 2 | Cumplimiento del código por capas | Cumple | Cumple | Inspección de dependencias, pruebas de dominio, casos de uso, transacciones y cuatro correcciones conservadas. |
| 3 | Integración mediante API REST | Cumple parcialmente | Cumple parcialmente | Contratos y persistencia locales aprobados; doce peticiones HTTP reales; compatibilidad histórica probada. Supabase Auth y Ollama reales no ejecutados. |
| 4 | Precisión y resultados predictivos | Cumple parcialmente | Cumple parcialmente | Inferencia real y nueva herramienta reproducible; precisión independiente aún no verificable sin corpus. |
| 5 | Procedimientos almacenados | Cumple parcialmente | Cumple parcialmente | Cinco funciones, seis triggers y bloques anónimos inventariados; migración probada. No hay procedimientos `CREATE PROCEDURE` ni especificación concreta del profesor. |

Evidencias de esta ejecución, no de ejecuciones históricas:

- [Árbol de directorios](evidencias/auditoria-final/arbol_directorios.txt).
- [Inventario de archivos y rutinas](evidencias/auditoria-final/inventario_revision.json):
  127 archivos Python inspeccionados mediante AST, sin importaciones prohibidas
  encontradas; catorce SQL examinados, incluidas las dos definiciones históricas
  de la misma función de validación. Esto es inspección estática, no una prueba
  universal de ausencia de acoplamiento dinámico.
- [Inferencias reales](evidencias/auditoria-final/predicciones_sklearn.json): tres
  entradas, resultados y probabilidades con huellas SHA-256 de los artefactos.
- [HTTP local](evidencias/auditoria-final/http_local.json): doce peticiones TCP
  contra Uvicorn con sklearn real, memoria y autenticación demo; respuestas completas.
- [Pruebas ejecutadas](evidencias/auditoria-final/pruebas.json): resultados de cada
  caso Python y resumen frontend. No incluye secretos ni sesiones reales.

### Mapa de capas

| Capa | Ruta | Responsabilidad | Archivos principales | Cumplimiento |
|---|---|---|---|---|
| Dominio | `src/domain/entities`, `value_objects`, `services` | Entidades, estados, reglas de contenido y validación independientes de frameworks | `solicitud.py`, `prediccion_contexto.py`, `seccion_salida.py`, `solicitud_service.py` | Cumple |
| Aplicación | `src/application/use_cases` | Orquestación y autorización de solicitudes, contexto, generación y versiones | `servicios_solicitud.py`, `predecir_contexto.py`, `generar_borrador.py`, `actualizar_borrador.py` | Cumple |
| Puertos de entrada | `src/application/ports/input` | Contrato de creación de solicitudes | `solicitud_use_case.py` | Cumple; los demás casos de uso son servicios públicos invocados por los controladores, no es necesario crear una interfaz abstracta por cada uno |
| Puertos de salida | `src/application/ports/output` | Repositorios, predictor, LLM, exportación y unidad de trabajo | `context_predictor.py`, `unidad_trabajo.py`, `generador_borrador.py`, `informe_repository.py` | Cumple |
| Adaptadores de entrada | `src/adapters/in/controllers`, `schemas`, `web` | HTTP, representación, validaciones del transporte y cliente React | `ia_controller.py`, `solicitud_controller.py`, `prediccion_response.py`, `web/services/iaService.js` | Cumple localmente |
| Adaptadores de salida | `src/adapters/out/ai`, `persistence`, `documents` | Implementaciones sklearn/Ollama, memoria/PostgreSQL y DOCX | `sklearn_context_predictor.py`, `ollama_adapter.py`, `postgres.py`, `exportador_docx.py` | Cumple localmente; proveedores externos no certificados |
| Infraestructura | `src/infrastructure`, `src/main.py` | Composición, configuración, autenticación e inyección | `container.py`, `settings.py`, `dependencies.py`, `auth/supabase.py`, `main.py` | Cumple; sin cambios de configuración |
| Herramientas de evaluación | `scripts`, `tests` | Evaluación offline y pruebas; no son dependencias del dominio o aplicación | `evaluar_predictor.py`, `test_evaluar_predictor.py` | Ubicación adecuada; no se movieron carpetas |

Las entidades y reglas no importan FastAPI, Pydantic, sklearn ni psycopg; aplicación
usa contratos de repositorio y unidad de trabajo. Memoria implementa rollback con
snapshots y PostgreSQL con transacciones/savepoints. Las reglas de generación y
control de versiones permanecen en aplicación; transporte, serialización, SQL y
servicios externos permanecen en sus adaptadores. El ensamblaje de implementaciones
se realiza en infraestructura. No se encontró una ubicación incorrecta demostrable
que justificara reorganizar el proyecto.

### Matriz de endpoints

`s` = solicitud, `p` = plantilla, `i` = informe, `v` = número de versión. Las
rutas completas usan los parámetros OpenAPI correspondientes. «Aprobado» significa
prueba local; los endpoints Auth usan dobles HTTP de Supabase, y generación usa
dobles del generador/Ollama. No equivalen a ejecución contra esos proveedores.

| Método | Ruta | Funcionalidad | HTTP esperado | Caso probado | Resultado | Archivo/prueba |
|---|---|---|---|---|---|---|
| GET | `/health` | Salud | 200 | Salud sin credenciales | Aprobado, también TCP | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos`; `http_local.json` |
| GET | `/openapi.json`, `/docs` | Contrato y documentación | 200 | Esquema y seguridad Bearer | Aprobado | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos` |
| GET | `/auth/config` | Modo de sesión/persistencia | 200 | Memory/mock | Aprobado, TCP | `http_local.json` |
| GET | `/auth/me` | Identidad y permisos | 200/401/403 | Token verificado, token inválido, perfil sin rol | Aprobado con proveedor simulado | `tests/test_auth.py::test_verified_identity_uses_database_roles_not_metadata`, `test_unverified_token_never_reaches_profile`, `test_missing_inactive_or_roleless_profile_denied` |
| POST | `/auth/login` | Inicio de sesión | 200/403/422 | Cookie HttpOnly, CSRF y campos indebidos | Aprobado con proveedor simulado | `tests/test_auth.py::test_login_refresh_logout_cookie_and_no_secret_reflection`, `test_cookie_endpoints_reject_csrf`, `test_http_cannot_assign_admin_or_reflect_password` |
| POST | `/auth/refresh` | Renovar sesión | 200/401 | Renovación y falta de cookie | Aprobado con proveedor simulado | `tests/test_auth.py::test_login_refresh_logout_cookie_and_no_secret_reflection` |
| POST | `/auth/logout` | Cerrar sesión | 204 | Borrado de cookie | Aprobado con proveedor simulado | `tests/test_auth.py::test_login_refresh_logout_cookie_and_no_secret_reflection` |
| GET | `/tipos-informe` | Catálogo de tipos | 200 | Cuatro tipos | Aprobado, también TCP | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos` |
| GET | `/areas` | Catálogo de áreas | 200/401 | Catálogo y acceso anónimo denegado | Aprobado, 401 también TCP | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos`, `test_errores_401_403_404_409_422` |
| GET | `/plantillas` | Plantillas por tipo | 200 | Filtro, estructura, versiones | Aprobado | `tests/test_estructura_borrador.py::test_plantilla_anterior_y_piloto_de_memoria`; `tests/test_piloto_v2.py::test_fuentes_minimas_ollama_edicion_recuperacion_y_exportacion` |
| GET | `/plantillas/{plantilla_id}/campos` | Campos de entrada | 200 | Campos obligatorios y tipos | Aprobado | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos` |
| POST | `/solicitudes` | Crear solicitud | 201/404/422 | Asunto, referencias y tipo inferido inactivo | Aprobado, también TCP | `tests/test_auditoria_criterios.py::test_tipo_inferido_de_plantilla_debe_existir_y_estar_activo`; `tests/test_api.py::test_validaciones_request` |
| POST | `/solicitudes/` | Alias de creación | 201 | Creación por alias oculto en OpenAPI | Aprobado, TCP | `http_local.json` |
| POST | `/solicitudes/completa` | Crear formulario atómico | 201/400/404 | Creación, obligatorios y rollback | Aprobado | `tests/test_catalogos_pmv1.py::test_completa_creacion_actualizacion_y_rollback`, `test_completa_rechaza_referencias_desconocidas` |
| PUT | `/solicitudes/{solicitud_id}/completa` | Actualizar formulario atómico | 200/400/403 | Guardado completo, inválido y usuario ajeno | Aprobado | `tests/test_catalogos_pmv1.py::test_completa_creacion_actualizacion_y_rollback` |
| GET | `/solicitudes/{solicitud_id}` | Recuperar solicitud | 200/403/404 | Solicitud propia/ajena/inexistente | Aprobado, 200 también TCP | `tests/test_api.py::test_errores_401_403_404_409_422`; `http_local.json` |
| PUT | `/solicitudes/{solicitud_id}` | Editar/cancelar | 200/409/422 | Edición y estados automáticos protegidos | Aprobado | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos`, `test_errores_401_403_404_409_422` |
| PUT | `/solicitudes/{solicitud_id}/valores` | Guardar valores | 200/400 | Número grande y obligatorios | Aprobado | `tests/test_auditoria_criterios.py::test_entero_grande_es_finito_y_se_integra_por_rest`; `tests/test_api.py` |
| GET | `/solicitudes/{solicitud_id}/contexto` | Recuperar contexto | 200 | Contexto nulo, pendiente, histórico y actual | Aprobado, también TCP | `tests/test_compatibilidad_predicciones.py`; `tests/test_catalogos_pmv1.py::test_asunto_solo_y_recuperacion_contexto` |
| POST | `/solicitudes/{solicitud_id}/predecir-contexto` | Inferir y persistir | 200 | sklearn real y metadatos | Aprobado, también TCP | `tests/test_auditoria_criterios.py::test_metadatos_describen_estimadores_reales_y_no_precision`; `http_local.json` |
| POST | `/solicitudes/{solicitud_id}/validar-prediccion` | Confirmación humana | 200 | Aceptar/corregir explícitamente | Aprobado, aceptación también TCP | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos`; `tests/test_piloto_v2.py`; `http_local.json` |
| POST | `/solicitudes/{solicitud_id}/generar-borrador` | Generar y guardar versión | 201/409/500 | Flujo, duplicado, fallo sanitizado y reintento | Aprobado con generador simulado | `tests/test_api.py::test_fallo_generador_devuelve_500_sin_detalles_y_permite_reintentar`, `test_flujo_completo_swagger_y_catalogos` |
| GET | `/solicitudes/{solicitud_id}/informe` | Recuperar informe por solicitud | 200/404 | Informe guardado e inexistente | Aprobado | `tests/test_piloto_v2.py::test_fuentes_minimas_ollama_edicion_recuperacion_y_exportacion`, `test_versiones_inexistentes_y_solicitudes_sin_informe` |
| GET | `/informes/{informe_id}` | Recuperar informe | 200/403/404 | Lectura, permisos y ausencia | Aprobado | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos`, `test_informe_de_otro_usuario_y_campos_obligatorios` |
| PUT | `/informes/{informe_id}` | Nueva versión editada | 200/400/409 | Edición, contenido inválido y versión obsoleta | Aprobado | `tests/test_api.py::test_flujo_completo_swagger_y_catalogos`, `test_informe_de_otro_usuario_y_campos_obligatorios` |
| GET | `/informes/{informe_id}/versiones/{numero_version}` | Versión histórica | 200/404 | Snapshot y versión inexistente | Aprobado | `tests/test_piloto_v2.py::test_fuentes_minimas_ollama_edicion_recuperacion_y_exportacion`, `test_versiones_inexistentes_y_solicitudes_sin_informe` |
| GET | `/informes/{informe_id}/versiones/{numero_version}/docx` | Exportar versión guardada | 200/401/403/404 | DOCX, versiones y permisos | Aprobado sin llamar a Ollama | `tests/test_piloto_v2.py::test_descarga_aplica_permisos_del_informe`, `test_fuentes_minimas_ollama_edicion_recuperacion_y_exportacion`, `test_versiones_inexistentes_y_solicitudes_sin_informe` |

Los servicios React siguen enviando las mismas rutas, cuerpos y métodos. No
comparan literalmente `SKLEARN_RF_IA_01`; usan el contrato de respuesta y `es_mock`.
Las dos pruebas nuevas de compatibilidad insertan predicciones en PostgreSQL
desechable, las recuperan desde otra unidad de trabajo y por REST, y comprueban
que `SKLEARN_RF_IA_01`/`SKLEARN_IA_01` y sus parámetros no se reescriban. La
respuesta antigua sin metadatos devuelve `algoritmos: {}`; la actual los conserva.

## B. Hallazgos con ubicación, evidencia y prioridad

| Código | Criterio | Problema y ubicación | Evidencia y consecuencia | Prioridad / situación |
|---|---|---|---|---|
| AUD-01 | 2 | Tipo inferido eludía validación activa, `src/application/use_cases/servicios_solicitud.py:62` | Regresión crear/actualizar y rollback en `tests/test_auditoria_criterios.py:22`; la versión corregida rechaza referencias inválidas | Alta; resuelto en `946738b`, conservado |
| AUD-02 | 3 | Desbordamiento al convertir entero a float, `src/domain/services/solicitud_service.py:34` | Prueba de entero de 401 dígitos por REST en `tests/test_auditoria_criterios.py:51` | Media; resuelto en `946738b`, conservado |
| AUD-03 | 4 | Identificador sugería algoritmo RF, `src/adapters/out/ai/sklearn_context_predictor.py:305` | Estimadores reales e inferencias con `LogisticRegression`; no cambia pesos ni resultados | Media; resuelto en `946738b`, conservado |
| AUD-04 | 5 | Función SQL admitía títulos solo blancos, `database/migrations/20260930_01_secciones_salida.sql:27` | Migración correctiva `database/migrations/20261023_01_validar_titulos_secciones.sql`, pruebas de blancos Unicode, idempotencia y rollback | Media; resuelto en `946738b`, conservado |
| AUD-05 | 4 | Faltaba herramienta offline reproducible para evaluar etiquetas independientes | Búsqueda en `scripts/` y documentación inicial; no se podía ejecutar una evaluación completa aportando un corpus | Media; resuelto con `scripts/evaluar_predictor.py` y pruebas |
| AUD-06 | 4 | No hay corpus independiente ni procedencia del entrenamiento; no hay umbral académico | Inventario, documentación y evidencia existente contienen ejemplos, no etiquetas de referencia independientes. Impide afirmar precisión | Alta académica; pendiente externo |
| AUD-07 | 4 | `Memorando` no pertenece a `modelo_tipo.classes_` | Artefacto `src/infrastructure/ai/models/modelo_tipo.joblib`; tres clases entrenadas frente a cuatro de catálogo | Media; pendiente de definición de cobertura y datos, sin reentrenamiento autorizado |
| AUD-08 | 5 | Solo funciones; requisito específico de procedimientos no definido | Inventario SQL: cero `CREATE PROCEDURE`; las operaciones actuales ya usan unidad de trabajo y transacciones | Media académica; pendiente aclarar alcance, sin rutina artificial |
| AUD-09 | 3 | Faltaba regresión explícita de lectura histórica tras el cambio de identificador | No había prueba de ida y vuelta PostgreSQL + REST con ambos identificadores | Media; cobertura añadida en `tests/test_compatibilidad_predicciones.py` |
| AUD-10 | 1–5 | Informe inicial carecía de árbol, matriz REST, metodología e inferencias guardadas | Documento inicial de `946738b`; evidencia insuficiente para la nueva entrega académica | Media; documentación y evidencias completadas |

## C. Acciones correctivas de esta revisión

| Problema | Justificación / cambio | Archivo | Prueba verificable | Estado |
|---|---|---|---|---|
| Sin evaluación reproducible | CLI recibe corpus etiquetado, valida formato/duplicados/procedencia, usa predictor existente, genera métricas y huellas sin sobrescribir archivos | `scripts/evaluar_predictor.py` | `tests/test_evaluar_predictor.py`: doce casos, incluidos errores deliberados y ejecución real de CLI | Implementado |
| Sin contrato de corpus ni interpretación | Documentar campos exactos, etiquetas, independencia declarada, métricas por clase y multietiqueta y límites | `docs/EVALUACION_PREDICTOR.md` | Formato ejercitado por la CLI en pruebas; no se proporciona corpus oficial ficticio | Implementado |
| Compatibilidad histórica sin regresión específica | Persistir y recuperar ambos identificadores con metadatos históricos/actuales, usando PostgreSQL y REST | `tests/test_compatibilidad_predicciones.py` | Dos casos parametrizados aprobados | Implementado; sin cambiar contratos de producción |
| Evidencia académica incompleta | Árbol real, inventario, doce peticiones TCP, tres inferencias reales y resultados de cada prueba | `docs/evidencias/auditoria-final/` y este informe | JSON generado de ejecuciones y JUnit de esta revisión | Implementado |

No se modificó código del PMV1 que ya cumplía. Las cuatro correcciones originales
siguen pasando sus diez regresiones. Los cinco `.joblib` y `model_config.json`
se compararon byte a byte con `946738b`: sin cambios. Se conserva creación y
recuperación de solicitudes, confirmación/corrección del contexto, formulario
atómico, generación con el proveedor configurado, edición versionada, lectura
histórica, permisos y exportación DOCX. La ejecución real de Ollama no se afirma.
No se declara terminado PMV2 ni PMV3.

### Pruebas de esta revisión

| Ejecución | Aprobadas | Fallidas | Omitidas | Observación |
|---|---:|---:|---:|---|
| Python con PostgreSQL 16 aislado | 260 | 0 | 19 | `NAXJI_TEST_PG_PORT=55433 .venv/bin/python -m pytest -q -ra`; incluye arquitectura, dominio, casos de uso, API, SQL, regresiones y herramienta predictiva |
| Frontend | 51 | 0 | 0 | `npm run test:frontend` |
| HTTP TCP contra Uvicorn | 12 comprobaciones | 0 | 0 | sklearn real, memoria, autenticación demo; evidencia JSON separada |
| Lint / build / diff | Tres comandos correctos | 0 | 0 | `npm run lint`, `npm run build`, `git diff --check` |

Las 19 omisiones son diez casos de Supabase real (Auth, catálogos y persistencia)
y nueve de generación Ollama real. El detalle exacto por caso y motivo está en
`pruebas.json`. Una advertencia Starlette/httpx de deprecación no impidió ejecutar
las pruebas. No se deshabilitaron afirmaciones ni se modificaron los tests anteriores.

## D. Recomendaciones relacionadas con los cinco criterios

1. Mantener la estructura y los puertos existentes; ejecutar sus pruebas cuando
   cambien dependencias o adaptadores. No se requiere reubicar carpetas.
2. Proporcionar el archivo `evaluacion_independiente.json` descrito en
   [EVALUACION_PREDICTOR.md](EVALUACION_PREDICTOR.md), junto con procedencia,
   responsables del etiquetado y evidencia de separación del entrenamiento.
   Acordar umbrales y cobertura por clase antes de interpretar aceptación.
3. Decidir si Memorando debe formar parte de la predicción automática; si se
   exige, obtener datos y autorización para un trabajo separado de entrenamiento.
4. Ejecutar las integraciones externas opt-in únicamente con acceso autorizado
   y datos de prueba. Las pruebas locales no certifican sesiones Supabase reales.
5. Confirmar si el criterio SQL admite funciones almacenadas. Si exige un
   procedimiento concreto, una opción justificable **solo tras esa confirmación**
   es `registrar_version_informe`: bloquear el informe, comprobar la versión
   esperada e insertar el snapshot atómicamente, invocado exclusivamente por el
   repositorio PostgreSQL como `SECURITY INVOKER`. Las reglas de contenido y
   autorización permanecerían en aplicación. La unidad de trabajo actual ya
   cubre atomicidad/concurrencia; no existe hoy una necesidad demostrada que
   justifique duplicarla con ese procedimiento, por lo que no se añadió SQL nuevo.
6. Revisar la migración ya existente antes de cualquier despliegue real. Su
   ejecución local preserva filas y revierte ante títulos anteriores inválidos;
   la revisión de datos reales y la aplicación en Supabase permanecen pendientes.

## E. Metodología y nivel de cumplimiento

Se usa una lista de cotejo nominal, sin ponderaciones del profesor. Un criterio
se marca «Cumple» si sus requisitos observables en el alcance solicitado tienen
evidencia suficiente; «Cumple parcialmente» si hay partes verificadas y pendientes;
«No cumple» ante incumplimiento demostrado sin resolver; «No verificable» si no
existe evidencia para ninguna de sus partes. Se muestran porcentajes de cantidad
de criterios, no una nota académica ni una medida de precisión del modelo.

- Cumple: 2 de 5 (40 %), criterios 1 y 2.
- Cumple parcialmente: 3 de 5 (60 %), criterios 3, 4 y 5.
- No cumple: 0 de 5 (0 %).
- No verificable como criterio entero: 0 de 5 (0 %). Dentro del criterio 4,
  el nivel de precisión independiente sí es **no verificable**.

No se convierten los parciales a una puntuación inventada ni se presenta un
«100 %» mezclando cumplimiento completo con parcial. La herramienta reduce una
carencia reproducible del criterio 4, pero no sustituye datos ni demuestra precisión.

## F. Limitaciones y recursos pendientes

- Faltan corpus independiente, etiquetas humanas, información de entrenamiento
  que permita excluir solapamiento y umbrales de aceptación. La nueva CLI acepta
  los datos cuando se suministren; sus tests sintéticos no son evaluación oficial.
- Las tres inferencias publicadas son ejemplos reales del modelo, sin etiquetas
  verdaderas ni métrica experimental. La probabilidad no demuestra calibración.
- Supabase Auth, catálogos remotos, persistencia real y Ollama `qwen2.5:7b` no se
  validaron en esta revisión. Los diecinueve casos externos permanecen omitidos.
- PostgreSQL fue exclusivo de pruebas en loopback; los dobles mínimos de Auth
  solo ejercitan SQL local. No se alteraron datos, roles, RLS ni credenciales reales.
- La migración correctiva de `946738b` no se aplicó a Supabase. Se verificaron
  idempotencia, transacción, rollback, conservación y coherencia Python/SQL local.
- No hay especificación de qué procedimiento almacenado exige el profesor.
  Funciones, triggers y bloques `DO` se distinguen en el inventario; no se inventó
  una rutina para aparentar cumplimiento.
- Se conservaron rama, configuración del entorno, Trello, diseño visual, contratos
  REST y modelos. No hubo reentrenamiento ni cambios de PMV ajenos a los criterios.
