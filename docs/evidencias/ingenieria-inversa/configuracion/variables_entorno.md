# Prompt 5 — Variables y precedencia verificadas

Main **4f4d294**, corte 27/11/2026. No se leen valores privados. [environment()](../../../../src/infrastructure/configuration/database.py) combina `.env` < `.env.local` < variables del proceso; desactiva interpolación de dotenv yno reescribe archivos. [Settings.from_env](../../../../src/infrastructure/configuration/settings.py), [DatabaseSettings.from_env](../../../../src/infrastructure/configuration/database.py), [RagSettings.from_values](../../../../src/infrastructure/configuration/rag.py) y [SupabaseAuthSettings.from_env](../../../../src/infrastructure/auth/supabase.py) son las fuentes efectivas.

| Familia | Nombres reales y función | Condición/valor del código |
| ---| ---| ---|
| Persistencia/identidad | `NAXJI_PERSISTENCE_MODE`, `NAXJI_AUTH_MODE` | memory/postgres; mock, disabled, supabase. SupabaseAuth requierePG. |
| DB privada | `NAXJI_DB_HOST`, `PORT`, `NAME`, `USER`, `PASSWORD`, `SSLMODE`, `CONNECT_TIMEOUT`, cada sufijo con prefijo `NAXJI_DB_` | Seis primeras obligatorias en modoPG; TLS require/verify-ca/verify-full; timeout 10 por defecto. No publicar contraseña ni URI con credenciales. |
| Auth | `NAXJI_SUPABASE_URL`, `NAXJI_SUPABASE_PUBLISHABLE_KEY`, `NAXJI_AUTH_ALLOWED_ORIGINS`, `NAXJI_AUTH_COOKIE_SECURE`, `NAXJI_AUTH_COOKIE_SAMESITE` | URLHTTPS, clave publicable, orígenes explícitos; Secure true y SameSite strict por defecto; none requiereSecure. |
| API | `NAXJI_CORS_ORIGINS`, `NAXJI_API_DOCS_ENABLED` | Sin comodines; docs true en Settings y false en Docker runtime preparado. No equivalen a disponibilidad del servicio. |
| Generación | `NAXJI_OLLAMA_BASE_URL`, `NAXJI_OLLAMA_MODEL`, `NAXJI_OLLAMA_TIMEOUT_SECONDS` | localhost 11434 de desarrollo, qwen2.5:7b, 300 segundos. |
| Documentos/Storage | `NAXJI_RAG_ENABLED`, `NAXJI_STORAGE_BUCKET`, `NAXJI_STORAGE_SERVICE_KEY`, `NAXJI_DOCUMENT_FORMATS`, `NAXJI_DOCUMENT_MAX_BYTES` | false, naxji-documentos, clave privada solo servidor, pdf/docx/txt,10485760 bytes. Requiere preparación autorizada del destino. |
| Embeddings | `NAXJI_EMBEDDING_MODEL`, `NAXJI_EMBEDDING_DIMENSION`, `NAXJI_EMBEDDING_TIMEOUT_SECONDS` | bge-m3:567m, 1024,120 segundos. Cambiar dimensión requiere otra migración, no hacerlo en este cierre. |
| Recuperación | `NAXJI_RAG_CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_CHUNKS`, `TOP_K`, `MIN_SIMILARITY`, `CONTEXT_CHARS`, `LEASE_SECONDS`, `PROCESSING_REVISION`, cada sufijo con prefijo `NAXJI_RAG_` | Defaults 1200,180,2000,6, 0.5,8000,1800, "1". Se validan rangos; no se presenta el umbral como calibración institucional. |
| Revisión | `NAXJI_PMV3_ENABLED` | false de fábrica; con activación requiere contratos y tabla de eventos preparados. |
| Frontend | `VITE_API_URL` | Pública al compilar,`/api` por defecto en [api.js](../../../../src/adapters/in/web/services/api.js)/[session.js](../../../../src/adapters/in/web/services/session.js). Nunca clavesprivadas `VITE_*`. |
| Contenedor | `PORT`, `FORWARDED_ALLOW_IPS` | [deploy/start.py](../../../../deploy/start.py):8000 y 127.0.0.1 por defecto; PORT 1–65535. |

QA: `NAXJI_TEST_PG_PORT`, `NAXJI_RUN_DB_TESTS`, `NAXJI_RUN_AUTH_TESTS`, `NAXJI_RUN_OLLAMA_TESTS`, `NAXJI_RUN_PMV2_AI_TESTS` y salidas `NAXJI_*_EVIDENCE_DIR` controlan ensayos y no constituyen secretos del frontend. Las 21 optativas se conservan omitidas enCI; no se habilitan contra servicios compartidos para esta documentación.

La tabla detallada anterior se conserva abajo como antecedente; se enlazan [ejemplos públicos](../../../../.env.example), [guía](../../../GUIA_CIERRE_Y_DEMO.md) y [preflight offline](../../../../deploy/preflight.py). Los defaults del código son ejemplos técnicos, no valores efectivos extraídos de un despliegue.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Variables sin secretos

Valores de ejemplo o predeterminados del código, nunca configuración privada extraída:

| Variable | Obligatoria / función | Ejemplo o predeterminado |
|---|---|---|
| NAXJI_PERSISTENCE_MODE | Selecciona repositorios | memory / postgres |
| NAXJI_AUTH_MODE | Para usuarios reales, supabase con PG | mock en memoria; disabled si PG sin configurar |
| NAXJI_DB_HOST | Con PG, host autorizado | HOST_PRIVADO |
| NAXJI_DB_PORT | Con PG | 5432 |
| NAXJI_DB_NAME | Con PG, base autorizada | BASE_AUTORIZADA |
| NAXJI_DB_USER | Con PG, rol privado backend | ROL_BACKEND |
| NAXJI_DB_PASSWORD | Con PG, secreto fuera de Git | valor privado, no ejemplo reutilizable |
| NAXJI_DB_SSLMODE | Con PG, TLS | require / verify-ca / verify-full |
| NAXJI_DB_CONNECT_TIMEOUT | Opcional, conexión acotada | 10 segundos |
| NAXJI_SUPABASE_URL | Auth o Storage reales | https://SU_PROYECTO.supabase.co |
| NAXJI_SUPABASE_PUBLISHABLE_KEY | Auth real, publicable/anon | clave publicable del entorno |
| NAXJI_AUTH_COOKIE_SECURE | Cookies en HTTPS | true; false solo HTTP local |
| NAXJI_AUTH_COOKIE_SAMESITE | Sesión y política del navegador | strict; none requiere Secure |
| NAXJI_AUTH_ALLOWED_ORIGINS | Orígenes de acciones de sesión | http://127.0.0.1:5173 en desarrollo |
| NAXJI_CORS_ORIGINS | Frontend separado, orígenes explícitos | https://FRONTEND_AUTORIZADO |
| NAXJI_API_DOCS_ENABLED | Mostrar Swagger/ReDoc/OpenAPI | true por compatibilidad; false en público si no se necesita |
| NAXJI_OLLAMA_BASE_URL | Servicio de IA del backend | http://localhost:11434 solo desarrollo; HTTPS privado estable en producción |
| NAXJI_OLLAMA_MODEL | Generación | qwen2.5:7b |
| NAXJI_OLLAMA_TIMEOUT_SECONDS | Límite generación | 300 |
| NAXJI_RAG_ENABLED | Activación documental explícita | false |
| NAXJI_STORAGE_BUCKET | Con RAG real, bucket privado existente | naxji-documentos |
| NAXJI_STORAGE_SERVICE_KEY | Con RAG real, solo backend | secreto privado fuera de Git |
| NAXJI_DOCUMENT_FORMATS | Formatos autorizados | pdf,docx,txt |
| NAXJI_DOCUMENT_MAX_BYTES | Tamaño de carga | 10485760 |
| NAXJI_EMBEDDING_MODEL | Embeddings | bge-m3:567m |
| NAXJI_EMBEDDING_DIMENSION | Coincide con vector(1024) | 1024 |
| NAXJI_EMBEDDING_TIMEOUT_SECONDS | Límite embeddings | 120 |
| NAXJI_RAG_CHUNK_SIZE | Segmentación en caracteres | 1200 |
| NAXJI_RAG_CHUNK_OVERLAP | Solapamiento | 180 |
| NAXJI_RAG_MAX_CHUNKS | Límite por documento | 2000 |
| NAXJI_RAG_TOP_K | Máximo de candidatos | 6 |
| NAXJI_RAG_MIN_SIMILARITY | Umbral coseno | 0.5, calibración independiente pendiente |
| NAXJI_RAG_CONTEXT_CHARS | Presupuesto de contexto | 8000 |
| NAXJI_RAG_LEASE_SECONDS | Reserva de procesamiento | 1800 |
| NAXJI_RAG_PROCESSING_REVISION | Cambiar exige reindexación | 1 |
| NAXJI_PMV3_ENABLED | Con migración/perfiles preparados | false |
| VITE_API_URL | Frontend, origen API sin secretos | /api local; origen HTTPS público del backend al compilar |

QA: `NAXJI_TEST_PG_PORT` solo para clúster desechable; `NAXJI_RUN_DB_TESTS`, `NAXJI_RUN_AUTH_TESTS`, `NAXJI_RUN_OLLAMA_TESTS` y `NAXJI_RUN_PMV2_AI_TESTS` son opt-in. Los directorios `NAXJI_*_EVIDENCE_DIR` los fija el verificador dentro de una salida nueva. No habilitar tests de Supabase compartido a partir de esta tabla.

La tabla funcional está en `GUIA_CIERRE_Y_DEMO.md`; valores de ejemplo en `.env.example`. Familias: modo de persistencia/auth, conexión PostgreSQL/TLS, Supabase publicable, bucket/clave privada Storage, CORS/orígenes, cookies, Ollama, embeddings/chunking/umbral y banderas RAG/PMV3/documentación.

Obligatorias condicionales: DB y Auth para persistencia real; Storage/embeddings/tablas para RAG; migración de eventos para PMV3. Mock/memoria son demostrativos. Ningún secreto backend debe comenzar con VITE_. El inventario automático enumera literales; los nombres construidos en DatabaseSettings/RagSettings están expresados en la guía. No se leyeron ni publicaron valores de `.env` para este informe.
