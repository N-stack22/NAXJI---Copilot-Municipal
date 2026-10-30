# Ejecutar y activar PMV2

La activación institucional no se ha realizado. No ejecute SQL sobre Supabase
compartido ni despliegue sin autorización específica para ese entorno.
Las pruebas de esta entrega crearon bases aleatorias en un contenedor local.

## Dependencias y configuración

Python 3.11+, Node/npm, PostgreSQL con pgvector y Ollama local. Desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-pmv2.txt
npm.cmd ci
ollama pull qwen2.5:7b
ollama pull bge-m3:567m
```

`requirements-pmv2.txt` permite instalar también las dependencias backend vigentes
sin restaurar el `requirements.txt` que ya estaba eliminado en esta copia local.
Mantiene scikit-learn 1.6.1, correspondiente a los modelos existentes.

Conserve `.env` y `.env.local`; incorpore únicamente las variables necesarias de
`.env.example`. Ningún secreto debe llevar prefijo `VITE_`. Para el entorno externo:

```dotenv
NAXJI_PERSISTENCE_MODE=postgres
NAXJI_AUTH_MODE=supabase
NAXJI_SUPABASE_URL=https://SU_PROYECTO.supabase.co
NAXJI_SUPABASE_PUBLISHABLE_KEY=SU_CLAVE_PUBLICABLE
NAXJI_STORAGE_BUCKET=naxji-documentos
NAXJI_STORAGE_SERVICE_KEY=SU_CLAVE_SERVICE_ROLE_PRIVADA
NAXJI_RAG_ENABLED=false
NAXJI_OLLAMA_BASE_URL=http://localhost:11434
NAXJI_OLLAMA_MODEL=qwen2.5:7b
NAXJI_OLLAMA_TIMEOUT_SECONDS=300
NAXJI_EMBEDDING_MODEL=bge-m3:567m
NAXJI_EMBEDDING_DIMENSION=1024
NAXJI_EMBEDDING_TIMEOUT_SECONDS=120
NAXJI_RAG_CHUNK_SIZE=1200
NAXJI_RAG_CHUNK_OVERLAP=180
NAXJI_RAG_TOP_K=6
NAXJI_RAG_MIN_SIMILARITY=0.5
NAXJI_RAG_CONTEXT_CHARS=8000
NAXJI_RAG_PROCESSING_REVISION=1
```

Reutilice sus `NAXJI_DB_*` y configuración Auth existentes. Para HTTP local,
`NAXJI_AUTH_COOKIE_SECURE=false`; para HTTPS, true. La clave de Storage es privada,
con acceso al bucket, no la clave publicable del frontend. El adaptador espera
credencial service_role utilizable como Bearer en la API Storage. No la registre
en evidencias ni la comparta en el chat.

## SQL: primero en base aislada

Para una base existente, confirme las migraciones previas del repositorio:

1. `database/migrations/20260930_01_secciones_salida.sql`.
2. `database/migrations/20261001_01_correspondencias_normativas.sql`.
3. `database/migrations/20261001_02_titulo_version.sql`.
4. `database/migrations/20261001_03_formato_documento.sql`.
5. `database/migrations/20261023_01_validar_titulos_secciones.sql`.
6. `database/migrations/20261030_01_documentos_rag.sql` (nueva).

No repita semillas institucionales ya aplicadas. No use
`NAXJI_database_schema_actual.sql` para reconstruir una base existente: ese archivo
solo se usa en los fixtures sobre bases recién creadas. La migración PMV2 instala
pgvector si falta, conserva su esquema si ya existe y requiere privilegios para
crear extensión/tablas y ajustar permisos. No contiene datos semilla.

Revise especialmente la retirada de SELECT directo a `versiones_informe` para
anon/authenticated: evita saltarse el control de acceso a las fuentes mediante Data
API. El frontend de este repositorio consulta FastAPI; otros consumidores directos
deben revisarse antes de aplicar. El rol PostgreSQL del backend necesita acceso a
tablas nuevas y el mecanismo RLS/BYPASSRLS usado por el backend existente.

Ejecute el archivo completo con un cliente SQL autorizado y después
`database/checks/20261030_verificar_pmv2.sql`. Las primeras tres consultas deben
devolver cero inconsistencias; las nuevas tablas deben tener RLS activado. Las
pruebas aisladas verifican tanto primera ejecución como repetición y preservación
de filas/versiones anteriores.

## Storage privado y activación externa pendiente

En un proyecto de prueba autorizado, cree explícitamente un bucket **privado**
con el nombre configurado. No se crea al arrancar. Revise sus permisos y evite
políticas que permitan descargas públicas/directas fuera del backend. La API
comprobará `public=false` en cada acceso. Ajuste también límites del bucket y del
proxy HTTP al límite documental configurado, sin superar los límites del servidor.

Después de revisar SQL, bucket y variables, cambie `NAXJI_RAG_ENABLED=true` y reinicie:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
# En otra terminal:
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

Abra `/docs` para el contrato o entre por la interfaz con una cuenta Supabase
activa y sus roles/área existentes. En **Documentos**:

1. Cargue TXT UTF-8, DOCX o PDF con texto, con procedencia/autorización de uso.
2. Procese el documento y confirme INDEXADO y número de fragmentos.
3. Consulte con un segundo usuario de otra área: un archivo PRIVADO debe quedar
   invisible; AREA solo debe ser visible en el área correcta; un revisor no carga
   ni procesa. Pruebe también el original y el fragmento usando sus endpoints.
4. Cree una solicitud, confirme contexto y elija una plantilla compatible.
5. En el paso 3 active **Elaborar con documentos autorizados**, aporte los datos
   conocidos y genere. Revise estado de recuperación, fuentes citadas y no citadas.
6. Guarde una edición; cambie una sección citada y compruebe TEXTO_MODIFICADO.
7. Recupere ambas versiones y descargue Word: fuentes y contenido deben coincidir
   con cada versión. Reindexar el documento no debe reescribir esos snapshots.

La prueba institucional completa de estos siete pasos, con Auth/Storage reales y
revisión humana, sigue pendiente; los dobles no la sustituyen.

## Repetir pruebas reales aisladas

El clúster debe ser exclusivamente de pruebas. Los fixtures conectan solo a
`127.0.0.1`, usuario `naxji_step3`, sin leer credenciales de `.env`, crean bases con
nombres aleatorios y las eliminan al finalizar. El puerto **no debe corresponder
a un PostgreSQL compartido**.

```powershell
docker run --detach --rm --name naxji-pmv2-tests-20261030 `
  -e POSTGRES_USER=naxji_step3 -e POSTGRES_HOST_AUTH_METHOD=trust `
  -p 127.0.0.1:55433:5432 pgvector/pgvector:pg18

# Esperar a que pg_isready confirme disponibilidad:
docker exec naxji-pmv2-tests-20261030 pg_isready -U naxji_step3

.\.venv\Scripts\python.exe -u scripts/verificar_pmv2.py --pg-port 55433 --ia-real
# Al terminar y revisar las evidencias:
docker stop naxji-pmv2-tests-20261030
```

`trust` se limita aquí a un contenedor desechable en loopback; no es configuración
institucional. Si el nombre/puerto ya están ocupados, inspeccione qué servicio los
usa; no lo elimine automáticamente. La imagen y modelos comprobados se registran
en evidencias. El runner guarda salidas y exit codes y deshabilita las pruebas
legacy que pudieran apuntar a servicios compartidos. El modo `--ia-real` ejecuta
solo las nuevas pruebas IA sobre las bases aisladas.

Comandos individuales:

```powershell
$env:NAXJI_TEST_PG_PORT='55433'
$env:NAXJI_RUN_DB_TESTS='0'
$env:NAXJI_RUN_OLLAMA_TESTS='0'
python -m pytest -q
npm.cmd run test:frontend
npm.cmd run lint
npm.cmd run build
git diff --check

$env:NAXJI_RUN_PMV2_AI_TESTS='1'
$env:NAXJI_PMV2_EVIDENCE_DIR='D:/NAXJI/docs/evidencias/pmv2'
python -m pytest -q tests/test_pmv2_postgres.py
python scripts/evaluar_rag.py --output docs/evidencias/pmv2/recuperacion-real.json
```

Sin puerto aislado, las pruebas PostgreSQL se omiten. Sin opt-in IA se omiten
embeddings/generación reales. El runner utiliza el Python que lo invoca; en esta
copia es `.venv/Scripts/python.exe`.

## Fallos y reintentos

- ERROR_CARGA: revise Storage y vuelva a enviar el mismo archivo; conserva el ID.
- ERROR_PROCESAMIENTO: revise servicio/modelo de embeddings y reintente procesar.
- PROCESANDO tras caída: espere el vencimiento y reintente. La reserva impide
  sobrescribir un intento más reciente; no publique manualmente índices parciales.
- CORPUS_VACIO: cargue/procese documentos autorizados de la revisión activa.
- SIN_RESULTADOS: revise consulta/pertinencia y calibre el umbral con consultas
  etiquetadas; no interprete el estado como fallo técnico ni certeza sobre el tema.
- CITA_DESCONOCIDA/CITA_INVALIDA: el borrador no se guardó; revise/reintente el modelo.
- Cambio de pesos, extracción o segmentación: cambie la revisión, reprocese y
  compruebe recuperación antes de usarlo. Los snapshots de versiones se conservan.

El procesamiento es síncrono con reserva recuperable, sin cola/worker permanente.
Un corpus grande puede necesitar un worker y mediciones de capacidad posteriores.
OCR, aprobaciones y publicación final controlada no forman parte de PMV2.
