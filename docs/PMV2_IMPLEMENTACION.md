# PMV2: documentos, RAG y fuentes por versión

Fecha de integración: 30/10/2026. Rama `integration/pmv2-rag`.
Base: `origin/audit/criterios-hexagonal-api-prediccion-sql`,
`ec02d2bc1e355bfa8cb0e7fc46ba85659a599d77`.
El fetch confirmó `main` en `b4c0f82301aae3bd21c494ad9bd4809beaff45dd`;
auditoría tiene tres commits adicionales y ninguno por detrás. Se conservaron sus
correcciones, la eliminación local preexistente de `requirements.txt` y las carpetas
Postman ajenas. No se publicaron cambios en main, Trello ni Supabase compartido.

## Brechas y entrega

| Historia | Brecha inicial | Implementación | Evidencia y límite |
|---|---|---|---|
| HU-003 | Sin biblioteca ni archivos privados | `/documentos`, carga/lista/detalle/original/procesamiento; validación PDF/DOCX/TXT, metadatos, ámbitos, Storage privado | `tests/test_pmv2.py`, `tests/frontend/pmv2.test.mjs`; Storage HTTP con doble, activación externa pendiente |
| HU-IA-02 | Generación sin recuperación | Extracción y offsets, fragmentación reproducible, bge-m3 local, vectores PostgreSQL, filtros anteriores al ranking, límite de contexto | `tests/test_pmv2_postgres.py`, `recuperacion-pgvector-real.json`; prueba real aislada |
| HU-IA-03 | Versiones sin sustento | Fuentes recuperadas frente a citadas, IDs validados, relación sección/versión, snapshots, invalidación al editar y Word desde versión guardada | `ollama-real.json`, pruebas API/DOM y PostgreSQL; revisión humana institucional pendiente |

## Arquitectura y flujo

- Dominio: `Documento`, regla `puede_leer`, snapshot opcional `VersionInforme.sustento`.
- Puertos: `DocumentoRepository`, `AlmacenDocumentos`, `ExtractorDocumentos`,
  `Embeddings`, `RecuperadorDocumentos`. `ContextoConfirmado.fuentes` lleva referencias
  autorizadas; `ResultadoBorrador.citas` identifica lo utilizado por el generador.
- Aplicación: `GestionDocumentos` valida, reserva, procesa y recupera;
  `GenerarBorrador` integra recuperación en el botón existente, valida citas y guarda
  informe/versión/citas/estado en la unidad de trabajo original.
- Adaptadores de salida: `DocumentosPostgres`, `AlmacenSupabase`,
  `ExtractorArchivos`, `EmbeddingsOllama`, generador y exportadores existentes.
- Entrada: controlador documental, contratos OpenAPI, biblioteca React y panel de fuentes.
- Infraestructura: `RagSettings` y composición explícita en `Container`.

Se mantienen React/JSX, Vite, FastAPI, PostgreSQL/Supabase Auth, scikit-learn y Ollama.
No se añade Qdrant ni se migra el frontend a TypeScript.

El recorrido conserva cuatro pasos: asunto → confirmación → elaboración → vista
previa. En el tercero, el usuario carga/procesa documentos y activa «Elaborar con
documentos autorizados». La biblioteca también tiene ruta autenticada independiente.
La consulta actual es el asunto guardado; no se permite elegir arbitrariamente áreas
o propietarios desde React. Las normas aceptadas en catálogo conservan su tratamiento
previo: seleccionarlas no equivale a disponer de su texto.

## Archivos y permisos

PDF con texto por página, DOCX con párrafos/tablas y TXT UTF-8. PDF cifrado,
corrupto o con alguna página sin texto se rechaza explicando el límite OCR;
no se genera contenido ficticio. No se inventa paginación DOCX/TXT. Se limitan
tamaño, expansión del ZIP, páginas, texto extraído y fragmentos. El límite ASGI
también limita el cuerpo antes del parser multipart. No se ejecuta contenido de archivos.

Se guardan título, nombre original saneado, tipo verificado, bytes, SHA-256,
propietario, fechas, procedencia declarada, ámbito, área derivada del perfil,
ubicación privada, estado, error y revisión de procesamiento. La ubicación y
reservas internas no se devuelven al cliente. La procedencia es declaración del
usuario; no constituye certificación de autorización institucional.

| Operación | Regla de servidor |
|---|---|
| Leer privado | Propietario o ADMINISTRADOR |
| Leer AREA | Lo anterior o perfil activo con esa misma área |
| Leer INSTITUCIONAL | Perfil activo con roles existentes |
| Cargar | FUNCIONARIO o ADMINISTRADOR; AREA exige área del perfil |
| Cargar INSTITUCIONAL | ADMINISTRADOR |
| Procesar/reintentar | Propietario con rol de escritura o ADMINISTRADOR |
| REVISOR/APROBADOR | Lectura autorizada; sin aprobación formal PMV3 |

La deduplicación usa propietario + ámbito + área + hash: no revela archivos
privados de otros usuarios. Repetir una carga devuelve el mismo documento dentro
de esa clave; prevalecen sus metadatos originales. Si falla Storage se reenvía el
mismo archivo y se reutiliza la ruta. Estados: SUBIENDO, ERROR_CARGA, CARGADO,
PROCESANDO, ERROR_PROCESAMIENTO, INDEXADO. Reservas con UUID y vencimiento impiden
publicar respuestas tardías. Los reintentos vencidos sustituyen el índice de forma
atómica; las filas anteriores no se usan mientras el documento no esté INDEXADO.
No hay borrado ni cambios de ámbito en este alcance.

Supabase Storage exige bucket existente con `public=false`; el adaptador lo
comprueba al escribir y leer, usa clave privada solo en backend, transmite originales
mediante endpoints autorizados y verifica hash al leer. No devuelve URLs públicas.
Los almacenes en memoria existen solo como dobles explícitos de pruebas.

## Recuperación y embeddings

Modelo separado de generación: **bge-m3:567m**, multilingüe, vectores de **1024**
dimensiones. Se verificaron documentación y ejecución de `POST /api/embed`, con
`input` como lista y `truncate=false`. El adaptador comprueba cardinalidad,
dimensión, valores finitos y norma positiva; normaliza antes de guardar/consultar.
La dimensión está fijada por `vector(1024)`; cambiarla exige migración y reindexación.
No se usa `qwen2.5:7b` para embeddings. Los digests usados están en `servicios.json`.

Fragmentación por unidad extraída, ventanas de caracteres de 1200 con solapamiento
180 por defecto, offsets sobre texto normalizado, máximo 2000 fragmentos. Cada
fragmento conserva localización, rango, ordinal y revisión. Su UUID depende del
documento, revisión, ordinal y hash del texto. La revisión incluye extractor,
segmentador, parámetros, modelo, dimensión y revisión administrada de pesos.
Al cambiar pesos/digest, incremente `NAXJI_RAG_PROCESSING_REVISION` y reprocese;
no mezcle vectores de revisiones diferentes.

La consulta usa **similitud coseno = 1 − distancia coseno**, mayor es mejor.
Valores iniciales: `top_k=6`, similitud mínima `0.5`, contexto máximo 8000 caracteres.
No se corta un fragmento silenciosamente; se omite si no cabe en ese presupuesto.
PostgreSQL materializa primero los documentos accesibles/indexados de la revisión
vigente y luego calcula/ordena con pgvector. Se elige búsqueda exacta para este
corpus piloto; no se usa ANN con filtros tardíos que puedan perder resultados
autorizados. El volumen institucional requiere medir latencia antes de adoptar ANN.

Estados diferenciados: CORPUS_VACIO (sin corpus procesado accesible de la revisión),
SIN_RESULTADOS (sin coincidencias sobre el umbral), RECUPERADO. Los fallos de DB,
Storage o embeddings devuelven errores técnicos; la generación se libera para
reintento y no guarda un borrador presentado como RAG exitoso. Una búsqueda vacía
puede producir borrador con advertencia explícita, sin fuentes fingidas.

## Citas y versiones

Con fuentes, Ollama recibe texto/título/procedencia/localización e identificadores
autorizados y devuelve `{secciones, citas:[{fragmento_id,seccion}]}`. Sin fuentes
conserva el contrato anterior. Se validan identificador y sección existente con
texto; el servidor añade `[F:UUID]` y conserva el pasaje realmente guardado. También
se validan marcadores escritos por el modelo: una fuente desconocida provoca 502
y no se guarda el informe. Las citas son asociaciones declaradas por el modelo,
**no una prueba automática de entailment, veracidad o vigencia normativa**.

`sustento` conserva todos los fragmentos recuperados y cuáles fueron citados,
con texto exacto, localización, hash, título, procedencia, revisión y puntuación.
`version_citas` relaciona versión, documento, fragmento, sección, pasaje y snapshot.
No tiene FK al índice mutable; reindexar no destruye la evidencia histórica.
La edición copia el snapshot y marca TEXTO_MODIFICADO en toda sección citada que
cambió. Las demás citas siguen PENDIENTE_REVISION, nunca «respaldo verificado».
Una cita retirada del texto conserva el vínculo histórico marcado para revisión.

Lectura y exportación aplican autorización del informe y acceso actual a cada
documento: los snapshots inaccesibles se ocultan. Originales y fragmentos comprueban
permisos nuevamente. Si RAG está desactivado, se ocultan los textos de sus fuentes.
Versiones históricas sin `sustento` siguen editándose/exportándose. Recuperar o
exportar usa el snapshot guardado, sin nueva búsqueda ni generación. Word añade
un anexo de referencias del piloto; no es exportación final controlada PMV3.

Las instrucciones documentales se tratan como datos no confiables; el prompt
mantiene reglas y esquema. Una norma o guía no aporta hallazgos del expediente.
«Sin resultados de inspección» sigue exigiendo verificación pendiente. Estas
medidas reducen errores; la revisión humana sigue siendo necesaria.

## SQL y contratos

Migración aditiva: `database/migrations/20261030_01_documentos_rag.sql`.
Añade documentos, fragmentos vectoriales, `versiones_informe.sustento` nullable y
citas, sin reconstruir tablas ni ejecutar semillas. Es transaccional/repetible.
Conserva pgvector si ya está en `extensions`, como en instalaciones Supabase.
No se aplican migraciones durante el arranque. Las pruebas verifican repetición
y conservación íntegra de registros previos, además del esquema `extensions`.

RLS activado en tablas nuevas y sin privilegios directos para anon/authenticated.
El backend usa el rol PostgreSQL existente con acceso requerido; su autorización
se aplica en aplicación y SQL antes del ranking. Se retira SELECT directo de
`versiones_informe` para evitar que Data API exponga snapshots sin comprobar las
fuentes; la API FastAPI conserva acceso. Revisar esa modificación si existen
clientes ajenos que consumen directamente la tabla. No se alteran los cuatro roles.

| Método y ruta | Entrada / salida |
|---|---|
| GET `/documentos/configuracion` | Habilitación, formatos y límites; autenticado |
| POST `/documentos` | Multipart archivo, título, procedencia, ámbito → metadatos, 201 |
| GET `/documentos?limite=100&offset=0` | Lista autorizada paginada |
| GET `/documentos/{id}` | Metadatos autorizados |
| POST `/documentos/{id}/procesar` | Proceso/reintento idempotente → metadatos |
| POST `/documentos/recuperar` | `{consulta}` → estado y fuentes |
| GET `/documentos/{id}/fragmentos/{fragmento}` | Fragmento vigente autorizado |
| GET `/documentos/{id}/original` | Binario privado; no-store |
| POST `/solicitudes/{id}/generar-borrador` | Añade `usar_documentos:boolean=false` al contrato existente |
| GET/PUT `/informes/...`, versiones y DOCX | Contrato anterior + sustento opcional guardado |

Errores: 400 archivo/datos inválidos; 401 autenticación; 403 rol/escritura;
404 inexistente o documento invisible; 409 reserva/concurrencia; 413 carga excesiva;
502 cita desconocida/inválida o salida de generación inválida; 503 servicios o
activación no disponibles; 504 timeout de Ollama. Los detalles externos y secretos
no se reflejan al cliente. OpenAPI ejecutable en `/docs` y `/openapi.json`.

## Fuentes técnicas consultadas

- [API de embeddings de Ollama](https://docs.ollama.com/api/embed).
- [BGE-M3 en Ollama](https://ollama.com/library/bge-m3).
- [Ficha del autor BAAI y dimensiones](https://huggingface.co/BAAI/bge-m3).
- [Descarga autenticada de archivos privados Supabase](https://supabase.com/docs/guides/storage/serving/downloads).

Activación y límites de validación: [guía](PMV2_GUIA_EJECUCION.md) y
[pruebas](PMV2_PRUEBAS.md). No se implementó revisión formal, aprobación/rechazo,
auditoría avanzada ni exportación final PMV3.
