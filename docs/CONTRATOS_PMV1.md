# Contratos del backend PMV1

Fuente de nombres, relaciones y estados: `NAXJI_database_schema_actual.sql`.
Este backend no modifica ese archivo, no crea tablas ni ejecuta migraciones/RLS.

## Correspondencia de agregados

| Modelo/puerto | Tablas y reglas de persistencia |
|---|---|
| `Solicitud` / `SolicitudRepository` | `solicitudes`; `usuario_id` referencia `perfiles.id`; UUID y cinco estados exactos del SQL |
| `Solicitud.valores` | `solicitud_valores`; contiene `id`, `solicitud_id`, `campo_plantilla_id`, `valor`, fechas; único por solicitud/campo |
| `Plantilla.campos` / `PlantillaRepository` | `plantillas` y `campos_plantilla`; conserva `tipo_informe_id`, `area_id`, versión, flags activo/activa y seis tipos de datos |
| `PrediccionContexto` / `PrediccionRepository` | `predicciones_ia`; predicciones originales, modelo/versión, confianzas, parámetros y validación |
| `PrediccionContexto.normativas` | `prediccion_normativas`; el `prediccion_id` se obtiene del agregado padre; único por predicción/normativa |
| `Informe` / `InformeRepository` | `informes`; `solicitud_id` único; referencia plantilla, autor, estado y título |
| `Informe.versiones` | `versiones_informe`; JSONB `contenido`, `numero_version`, `origen`, autor, modelo y metadatos; único por informe/número |
| `UsuarioActual` | Proyección de identidad autenticada, `perfiles`, `usuario_roles` y `roles`; no se persiste por este backend |
| `CatalogoRepository` | Proyecciones mínimas de `tipos_informe`, `areas_municipales`, `normativas` |

Los modelos son proyecciones de PMV1, no copias exhaustivas de cada columna SQL.
Las columnas omitidas conservan defaults o se manejan en el adaptador. Al actualizar,
un adaptador real debe preservar las columnas ajenas a esta proyección. Fechas de
dominio usan UTC; los adaptadores deben devolver los valores efectivos de la BD.

`descripcion` no es columna de `solicitudes`. Antecedentes y detalle pertenecen a
`solicitud_valores`, vinculados a campos reales de la plantilla. Los campos de demo
no afirman que existan registros equivalentes en Supabase.

La confirmación conserva la propuesta original en `predicciones_ia`; los IDs finales
se guardan en `solicitudes.tipo_informe_id` y `area_destino_id`. Cada normativa guarda
su aceptación. La instantánea del asunto utilizado se incluye en el JSONB existente
`parametros.asunto` para detectar predicciones obsoletas, sin agregar columnas.

El contenido se almacena exclusivamente en las versiones. `InformeResponse` es una
proyección HTTP que combina la cabecera del informe y su última versión.

## Puertos y sustitución de adaptadores

El punto de composición es `src/infrastructure/configuration/container.py`.
Dominio y casos de uso no importan FastAPI, Supabase, Ollama, sklearn ni clientes HTTP.
Los schemas Pydantic pertenecen al adaptador de entrada.

- `SolicitudRepository`: obtener UUID y guardar agregado con valores; guardar no cambia IDs.
- `PlantillaRepository`: listar y obtener cabecera con campos.
- `CatalogoRepository`: tipos, áreas y normativa por UUID.
- `PrediccionRepository`: guardar agregado y recuperar la última predicción de una solicitud.
- `InformeRepository`: obtener por informe/solicitud y guardar cabecera/versiones.
- `UnidadTrabajo`: todas las escrituras relacionadas se confirman juntas o se revierten.
  Debe impedir duplicados y pérdidas de edición concurrentes. Los repositorios que
  participan deben usar la misma transacción/sesión que esta unidad de trabajo.
- `ContextPredictor.predecir(asunto, solicitud_id)`: devuelve `PrediccionContexto` con
  referencias existentes del catálogo, modelo identificable, confidencias 0..1 y normativas.
- `GeneradorBorrador.generar(asunto, plantilla, datos, contexto, instrucciones)`:
  recibe datos por clave de campo y contexto confirmado, devuelve `ResultadoBorrador`.
  El JSON debe incluir textos no vacíos `antecedentes`, `desarrollo`, `conclusiones`;
  puede agregar otras secciones/datos. Fallos previstos del proveedor se traducen a
  `ErrorGeneracion`; no deben incorporar secretos al mensaje HTTP.

Las firmas exactas están en `src/application/ports/output/`. La integración externa
debe adaptar su respuesta a esos contratos; no requiere cambiar los casos de uso.
El adaptador Ollama anterior implementa otro puerto y queda conservado e inactivo.

## Semántica del mock y decisiones de PMV1

- Las cuatro clases de informe y los cuatro roles usan códigos presentes en el SQL.
- Todos los UUID de fixtures son ficticios y deterministas; no deben insertarse como
  si fueran IDs existentes en Supabase. Hay cuatro plantillas demo y dos áreas demo.
- La predicción es fija para probar la API y se identifica como `MOCK_CONTEXT_PREDICTOR`.
  No evalúa la sumilla. La norma ficticia no constituye información normativa real.
- `configuracion.opciones` es la convención demo de select. El SQL permite JSON libre;
  el equipo de plantillas debe mantener esa convención o adaptar su representación.
- Si una plantilla tiene `area_id`, PMV1 exige que coincida con `area_destino_id`.
  Es una regla de aplicación de esta demo, no un CHECK ni una deducción del SQL.
- La unidad memory usa exclusión mutua y snapshots. La generación es síncrona y el
  bloqueo se mantiene durante la llamada al mock. Para proveedores lentos, evaluar
  transacciones/bloqueos reales y tiempos máximos al implementar el adaptador.
- Los cuatro roles existen como valores de dominio. En PMV1 funcionario/admin
  elaboran; revisor/aprobador solo leen recursos propios. La política final y RLS
  pertenecen al equipo responsable, y todavía no se han integrado.
- No hay sesiones reales, colas, revisión/aprobación, exportación, RAG ni auditoría.
  Las versiones implementadas responden al guardado requerido por el SQL y PMV1.

## Diagnóstico previo y reutilización

La base ya permitía crear/consultar solicitudes con IDs enteros y un diccionario,
validaba asunto/descripcion y exponía `/health`. Se conservaron las capas, el patrón
de repositorio, la validación de cadenas, los casos de uso y la respuesta de salud.

Se corrigieron IDs, estados y campos para ajustarlos al SQL. Se extrajeron schemas y
composición fuera de los controllers; se añadieron permisos, catálogos, valores,
contexto confirmado, versiones, errores y pruebas. El remoto contenía un commit
Ollama que se incorporó antes de editar; sus archivos de adaptador/puerto originales
se conservaron. El controller previo no estaba registrado en main y el caso de uso
de generación se adaptó al flujo estructurado solicitado.
