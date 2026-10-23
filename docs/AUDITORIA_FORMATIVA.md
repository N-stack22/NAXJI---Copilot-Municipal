# Evaluación formativa de arquitectura, API, predicción y SQL

Fecha: 2026-10-23. Repositorio: `N-stack22/NAXJI---Copilot-Municipal`.
Base: `b4c0f82301aae3bd21c494ad9bd4809beaff45dd`.
Rama de revisión: `audit/criterios-hexagonal-api-prediccion-sql`.

Esta evaluación usa los cinco enunciados proporcionados, no una rúbrica detallada
del profesor ni un umbral de precisión supuesto. «Cumple» significa que los
requisitos observables descritos aquí se verificaron; no certifica los servicios
externos ni requisitos académicos adicionales no especificados.

## Resultados

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
entrenados. Los cambios se dejan sin commit ni push para revisión en la rama indicada.

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
