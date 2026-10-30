# Pruebas PMV2 — 30/10/2026

La validación distingue implementación, dobles, servicios reales aislados y
activación externa. No se escribió en Supabase compartido ni se desplegó.
Las salidas completas y códigos de salida están en
[`evidencias/pmv2/checks.json`](evidencias/pmv2/checks.json).

## Resultados y alcance

| Comprobación | Resultado de referencia | Alcance |
|---|---|---|
| `python -m pytest -q`, PostgreSQL aislado habilitado | 295 aprobadas, 21 omitidas | Regresiones PMV1 + PMV2; pgvector real, proveedores IA/Storage con dobles salvo opt-in |
| `npm run test:frontend` | 52 aprobadas | React/JSDOM y HTTP simulado; cuatro pasos, documentos, reintentos, fuentes, ediciones y versiones |
| `npm run lint` | Aprobado | ESLint |
| `npm run build` | Aprobado | Vite producción |
| `git diff --check` | Aprobado | Espacios y conflictos; advertencias CRLF de Git en Windows no son errores |
| `tests/test_pmv2_postgres.py` con IA habilitada | 6 aprobadas | Migraciones, persistencia, esquema extensions, concurrencia, IA real y evaluación de recuperación |

La suite sin IA omite las dos nuevas pruebas reales opt-in y 19 verificaciones
externas legacy: nueve de Supabase DB/catálogos, una de Auth real y nueve de Ollama.
Las dos PMV2 se ejecutaron después en la suite real de seis pruebas. Los motivos
por archivo están en `pytest.txt` con la opción adicional `-rs`.
No se habilitan pruebas contra Supabase compartido. Las pruebas
del recorrido DOM se ejecutan con respuestas HTTP simuladas: no se presentan como
navegador real conectado a Supabase. Auth, Storage y la clasificación del recorrido
IA real utilizan dobles explícitos; PostgreSQL, pgvector, bge-m3 y qwen son reales.
El clasificador sklearn existente conserva sus pruebas de regresión propias.

## Historias y criterios verificables

| Criterio | Prueba/evidencia | Observación |
|---|---|---|
| HU-003: PDF/DOCX/TXT válidos, corruptos, vacíos y OCR | `test_extraccion_pdf_docx_txt_y_localizaciones`, `test_archivos_invalidos`, `test_pdf_ocr_explicito` | PDF sintético con texto real y sin texto; DOCX con tabla; TXT UTF-8 |
| Límites antes de persistir y del parser | `test_validacion_limites_formatos_y_no_guarda_invalido`, `test_limite_carga_antes_del_parser_y_sin_content_length` | No quedan metadatos ni archivos de entradas inválidas |
| Privacidad, áreas y roles | `test_permisos_usuario_area_roles_y_originales`, `test_sql_preserva_primera_repeticion_persistencia_y_filtros` | API/dominio/SQL; no se afirma validación de permisos Storage reales |
| Storage privado, errores sanitizados | `test_storage_rechaza_bucket_publico_y_sanitiza_error`, `test_storage_contrato_carga_lectura_privada_y_limite` | HTTP con doble; bucket público se rechaza; carga y GET autenticado con límite de descarga |
| Duplicados, hash y reintentos | `test_deduplicacion_privada_y_reintentos_idempotentes`, `test_reintento_storage_no_duplica_y_hash_integridad` | Misma clave→mismo ID; otros usuarios→IDs distintos |
| HU-IA-02: extracción, offsets y segmentación | `test_segmentacion_reproducible_offsets_y_limite` | Ventanas reproducibles y procedencia sin páginas inventadas |
| Embeddings API/dimensión/finito/norma | `test_embeddings_contrato_real_api_con_doble_http`, `test_embeddings_api_valida_dimension_numeros_y_norma` | Más prueba contra modelo local de 1024 dimensiones |
| Migración primera/repetición/conservación | fixture `pmv2_db`, `test_pgvector_instalado_en_extensions_conserva_esquema` | DB aleatoria, snapshots previos idénticos salvo nueva columna nullable |
| Recuperación vacía, negativa, pertinente o caída | `test_recuperacion_vacia_negativa_pertinente_y_fallo`, `test_generacion_sin_fuentes_identifica_resultado_y_advierte` | Estados separados; error técnico no se degrada a generación sin fuentes |
| Índice persistente y publicación por intento | `test_pg_reservas_no_permiten_resultado_tardio`, `test_concurrencia_procesamiento_y_respuesta_tardia` | Conflicto y respuesta tardía rechazados; índice sin duplicación |
| HU-IA-03: fuentes dentro de generación | `test_api_recorrido_con_citas_edicion_recuperacion_y_docx`, `ollama-real.json` | Prompt con fragmentos y guardado de citas por versión |
| ID desconocido/sección inválida | `test_cita_desconocida_y_recuperacion_caida_no_guardan`, `test_citas_estructuradas_usadas_y_no_usadas` | Error, reserva liberada y ausencia de informe guardado |
| Sin resultados de inspección e instrucciones en fuente | `test_sin_resultados_no_se_convierte_en_inspeccion_por_rag` | El esquema conserva prefijo pendiente; datos inyectados no son instrucciones de sistema |
| Edición, reindexación, recuperación y exportación | `test_pg_citas_versiones_edicion_recuperacion_atomica` | Fuente histórica estable; nueva versión marca cambios; exportar con IA caída funciona |
| Acceso actual a fuentes históricas | `test_fuente_sin_acceso_no_expone_snapshot` | Redacción de snapshot sin mutar el persistido |
| Frontend biblioteca y errores | `tests/frontend/pmv2.test.mjs` | Carga multipart, procesamiento fallido/reintento, conservación de título, fuentes citadas/no citadas y escape HTML |
| Frontend PMV1 y tardías | `tests/frontend/nuevoInforme.test.mjs` | Piloto v1/Anexo08, cuatro pasos, envío usar_documentos, versiones y descargas guardadas |

## Recuperación real y calibración

Corpus **NAXJI-PMV2-SINTETICO-01**: tres textos ficticios identificados en
[`tests/fixtures/pmv2_corpus.json`](../tests/fixtures/pmv2_corpus.json): residuos en
parques, impuesto predial y licencias de edificación. Ocho consultas etiquetadas:
seis positivas, dos negativas sobre antibióticos y repostería. Hash del corpus,
rankings, puntuaciones y versiones de servicios están en evidencias.

Embeddings reales `bge-m3:567m`, dimensión 1024; consultas en español. El script
`scripts/evaluar_rag.py` compara umbrales 0.4, 0.5, 0.55, 0.6, 0.65 y 0.7 y
top_k 1/3/6 con coseno exhaustivo en Python. La prueba
`test_evaluacion_recuperacion_pgvector_real` repite las ocho consultas mediante
el adaptador SQL de producción, con documentos procesados y vectores reales.

| Configuración | Resultado en el corpus sintético |
|---|---|
| Similitud mínima 0.5, top_k 6 | Hit@1 6/6; recall macro 1.0; precisión macro 1.0; negativas rechazadas 2/2 |
| Similitud mínima 0.4, top_k 6 | Recall 1.0; precisión macro ≈0.389: entran referencias de otros temas |
| Similitud mínima 0.65 | Recall 0.5; se pierden tres consultas pertinentes |
| Similitud mínima 0.7 | Recall 0.0 |

Se conserva 0.5 como valor inicial configurable. Los resultados no representan
precisión del RAG institucional: corpus pequeño, etiquetas sintéticas, sin conjunto
independiente ni revisión de especialistas. No se reutilizan métricas del clasificador.
Hace falta calibrar con documentos autorizados y consultas municipales reales.

## Recorrido real, intentos y citas

[`ollama-real.json`](evidencias/pmv2/ollama-real.json) registra un recorrido API:
carga 201 → procesamiento 200 → recuperación pgvector → generación qwen2.5:7b 201
→ edición 200 → ambas versiones recuperadas 200 → Word 200. La prueba utiliza
una guía ficticia, sin resultados de inspección, y exige al menos una fuente
efectivamente citada. No se mantuvieron conexiones de DB durante inferencia.

Se conservan resultados previos que motivaron correcciones:

- `ollama-real-consulta-sin-coincidencias.json`: la consulta con prefijo de prueba
  quedó bajo 0.5; el resultado se guardó como SIN_RESULTADOS, sin fingir fuentes.
- `ollama-real-recuperada-sin-citar.json`: documento recuperado pero cero citas.
  Se mantuvo la distinción y se mejoró el contrato estructurado del modelo.
- `ollama-real-cita-invalida-rechazada.json`: un contrato experimental con copias
  literales hechas por el modelo falló y devolvió 502 sin guardar. En el contrato
  definitivo el modelo declara fuente/sección y el servidor toma el pasaje y texto
  fuente exactos, evitando reconstrucciones inexactas de esos textos por el modelo.

La asociación por UUID/sección y el texto del snapshot se validan automáticamente.
La correspondencia semántica necesita revisión humana: en la salida sintética una
cita puede acompañar una afirmación genérica de ausencia de antecedentes; eso no
demuestra que la fuente sustente cada afirmación de la sección. No se informa una
«precisión de citas» humana inventada. **Revisión humana institucional realizada:
ninguna en esta sesión; pendiente**. Las citas quedan PENDIENTE_REVISION o
TEXTO_MODIFICADO y el producto lo advierte.

## Activación y verificaciones aún pendientes

1. Aplicación autorizada del SQL y comprobaciones en el entorno externo.
2. Bucket privado Supabase real, lectura/escritura persistente y recuperación tras
   reinicio con credencial de backend; no se utilizó el bucket compartido.
3. Supabase Auth/perfiles/áreas/roles reales sobre documentos y snapshots, incluidos
   intentos de acceso directo por Data API/Storage y revocación de acceso a un área.
4. Recorrido en navegador con frontend, backend, Auth, Storage y datos institucionales
   reales en un entorno de prueba autorizado; la prueba DOM usa HTTP simulado.
5. Corpus municipal autorizado, etiquetas independientes, pertinencia y revisión
   humana de las citas, además de medición de capacidad/latencia.

La implementación está integrada y verificada por capas y por API real aislada.
La aceptación institucional completa del PMV2 depende de estas verificaciones;
no se declara activado ni universalmente veraz.
