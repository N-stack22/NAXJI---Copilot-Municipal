# Ejecución, activación y demostración

Código en la rama `feature/finalizacion-pmv-trazable`, creada desde main `d99f960`. No hubo push, merge, despliegue ni escrituras en Supabase compartido. Los `.env` existentes no se sobrescribieron.

## Instalación canónica

Entorno verificado: Python 3.11 en Windows; versiones runtime en `requirements-runtime.lock.txt`; frontend en `package-lock.json`. El wheel se instaló en un venv nuevo y se importó fuera del repositorio. `requirements.txt` instala el proyecto completo; `requirements-pmv2.txt` conserva una entrada compatible. `requirements-db.txt` y `requirements-export.txt` son entradas históricas parciales.

PowerShell, desde esta rama:

```powershell
python -m venv .venv-local
.\.venv-local\Scripts\python.exe -m pip install -r requirements-runtime.lock.txt
.\.venv-local\Scripts\python.exe -m pip install --no-deps -e .
npm ci
```

Ubuntu, con Python 3.11 y Node/npm ya instalados:

```bash
python3.11 -m venv .venv-local
. .venv-local/bin/activate
python -m pip install -e .
npm ci
```

El lock runtime se obtuvo en Windows: validar sus marcadores y la instalación en Linux antes de desplegar. La creación de entornos sigue la [documentación de Python](https://docs.python.org/3.11/library/venv.html). No copie una carpeta venv entre sistemas.

## Demostración local sin servicios compartidos

Para PMV1/PMV3 en memoria, fije las variables en el proceso, sin sustituir archivos privados:

```powershell
$env:NAXJI_PERSISTENCE_MODE="memory"
$env:NAXJI_AUTH_MODE="mock"
$env:NAXJI_RAG_ENABLED="false"
$env:NAXJI_PMV3_ENABLED="true"
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

En otra terminal, `npm run dev -- --host 127.0.0.1`. Abra `http://127.0.0.1:5173`. Ollama local debe tener `qwen2.5:7b` para generar; `bge-m3:567m` se usa en las pruebas RAG reales. En Ubuntu use `export NAXJI_...=...` para las mismas variables.

1. Ingrese como funcionario demo. Use un asunto ficticio y confirme el área «Subgerencia de Ecología y Medio Ambiente» para coincidir con el revisor demo. Seleccione una plantilla, guarde datos y genere.
2. Edite y guarde. Abra «Revisión e historial» desde el informe; envíe la última versión.
3. Cierre sesión e ingrese como «Revisor PMV3 (identidad independiente)». Abra el informe, revise cada alerta y fuente; corrija y guarde una nueva versión si corresponde.
4. Registre el motivo y justificaciones por sección. Apruebe o rechace. No hay segunda etapa con APROBADOR.
5. Como funcionario, consulte versiones, autor/fecha/estado y descargue Word/PDF de la versión aprobada. Una rechazada devuelve 409 al exportar.
6. Como administrador, consulte auditoría. Otros roles reciben 403. El administrador no aprueba por el solo hecho de ser administrador.

Las identidades mock son temporales. La memoria desaparece al reiniciar. Esta demo no demuestra Auth, Storage o aprobación institucional.

## PostgreSQL/pgvector desechable y pruebas

Instale primero las herramientas QA con `python -m pip install -r requirements-test.txt`; para auditorías/build use `requirements-audit.txt`. psutil mide el proceso del arnés/API, no pertenece al backend runtime.

Utilice un contenedor propio y un puerto libre; no ejecute contra la base institucional. Ejemplo para crear uno **nuevo**:

```bash
docker run -d --name naxji-cierre-qa -p 127.0.0.1:15432:5432 -e POSTGRES_USER=naxji_step3 -e POSTGRES_HOST_AUTH_METHOD=trust pgvector/pgvector:pg18
python scripts/verificar_cierre.py --pg-port 15432 --ia-real --salida docs/evidencias/mi-verificacion-nueva
python scripts/carga_750_aislada.py --pg-port 15432 --concurrencia 4 --salida docs/evidencias/mi-carga-nueva
```

La autenticación trust corresponde exclusivamente a ese contenedor de laboratorio en loopback. Los fixtures crean y eliminan bases aleatorias nuevas. El arnés no acepta un hostname externo. Cada salida debe ser nueva: no sobrescriba evidencia histórica. `--ia-real` requiere los dos modelos locales; omítalo para la suite determinista. Las pruebas Supabase siguen desactivadas.

## Activación real en un entorno autorizado

Primero revise todas las migraciones aditivas de `database/migrations/` en el orden de sus nombres. La nueva es `20261126_01_pmv3_revision.sql`. Las semillas complementarias Legal/Memorando son pilotos optativos, no formatos oficiales ni reentrenamiento ML. La aplicación no ejecuta migraciones al arrancar.

| Variables backend | Valor/condición |
|---|---|
| `NAXJI_PERSISTENCE_MODE`, `NAXJI_AUTH_MODE` | `postgres`, `supabase` para uso persistente real |
| `NAXJI_DB_HOST/PORT/NAME/USER/PASSWORD/SSLMODE` | Valores privados del entorno autorizado; TLS `require` o verificación superior; nunca `VITE_` |
| `NAXJI_SUPABASE_URL`, `NAXJI_SUPABASE_PUBLISHABLE_KEY` | URL HTTPS del proyecto y clave publicable/anon; Auth no acepta una service_role |
| `NAXJI_STORAGE_BUCKET`, `NAXJI_STORAGE_SERVICE_KEY` | Bucket existente **privado**, clave privada solo backend; Storage exige HTTPS |
| `NAXJI_RAG_ENABLED` | `true` tras comprobar tablas, extensión vector, bucket y permisos |
| `NAXJI_EMBEDDING_MODEL/DIMENSION` | `bge-m3:567m`, `1024`; no cambiar dimensión sin migración |
| `NAXJI_OLLAMA_BASE_URL/MODEL` | Endpoint del servicio IA accesible desde el backend; `qwen2.5:7b` |
| `NAXJI_PMV3_ENABLED` | `true` después de aplicar la migración y asignar perfiles/áreas/roles |
| `NAXJI_CORS_ORIGINS`, `NAXJI_AUTH_ALLOWED_ORIGINS` | Orígenes concretos del frontend, sin comodín |
| `NAXJI_AUTH_COOKIE_SECURE` | `true` en HTTPS |
| `NAXJI_AUTH_COOKIE_SAMESITE` | `strict` por defecto; `none` solo con Secure cuando se necesite sesión entre sitios distintos |
| `NAXJI_API_DOCS_ENABLED` | `false` si el despliegue público no necesita Swagger/OpenAPI |
| `NAXJI_OLLAMA_TIMEOUT_SECONDS`, `NAXJI_EMBEDDING_TIMEOUT_SECONDS` | Límites explícitos; comenzar por los valores de `.env.example` y medir |
| `NAXJI_RAG_CHUNK_SIZE/CHUNK_OVERLAP/MAX_CHUNKS/TOP_K/MIN_SIMILARITY/CONTEXT_CHARS/LEASE_SECONDS/PROCESSING_REVISION` | Conservar inicialmente 1200/180/2000/6/0.5/8000/1800/1; calibrar con corpus propio |

La tabla de eventos tiene RLS y no concede acceso público. El rol privado del backend debe disponer de acceso efectivo a tabla/secuencia y una configuración RLS revisada. No publique ese rol como clave de navegador. Los perfiles se consultan en cada petición: retire roles o desactive el perfil para comprobar revocación. No se crea un módulo de administración de usuarios nuevo.

`GET /health` conserva el contrato de proceso. `GET /ready` exige administrador y comprueba disponibilidad de lectura/modelos/tablas/bucket con tiempos acotados. Un 200 no certifica todas las políticas RLS ni aceptación humana.

## Railway y Cloudflare Pages: preparación, sin despliegue

El dominio informado `naxji.pages.dev` corresponde a Cloudflare Pages. Backend: módulo `src.main:app`; ejecute Uvicorn enlazado a `0.0.0.0` y al puerto asignado por el entorno. El frontend usa `npm run build`, salida `dist`, y `VITE_API_URL` apuntando al origen HTTPS del backend o al proxy `/api`. Consulte las guías oficiales de [Railway/FastAPI](https://railway.com/guides/fastapi) y [Cloudflare Pages/React](https://developers.cloudflare.com/pages/framework-guides/deploy-a-react-site/).

Para producción no use localhost/ngrok como servicio IA: falta disponer de un endpoint privado estable autorizado. Prefiera mismo sitio o proxy controlado para la sesión; con sitios distintos, `SameSite=None` requiere `Secure`, y la política del navegador puede bloquear cookies de terceros aun así. Véase [Set-Cookie en MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie). CORS y origen CSRF deben enumerar el frontend real. No se verificó ese recorrido en producción.

## Revisión de fuentes y límites

Cargar no equivale a procesar. Confirme estado `INDEXADO`, pulse actualizar y genere una versión nueva con documentos autorizados. Versiones previas no recuperan fuentes retroactivamente. Un PDF mixto sin texto en alguna página se rechaza completo: aplique OCR externo y vuelva a cargar la copia corregida. Repetir el mismo archivo no añade texto.

Los marcadores citan fragmentos, no prueban vigencia o hechos del caso. Para aprobación, el revisor debe contrastar las secciones y justificar cada advertencia; las fuentes inaccesibles bloquean la aprobación. La exportación usa snapshots guardados y permisos actuales, sin llamar IA. La consulta histórica muestra `NO_REGISTRADO` cuando una versión anterior no tiene eventos de estado.

Rollback técnico: desactive PMV3/RAG y vuelva al commit anterior mediante el procedimiento autorizado, conservando tablas/versiones/eventos. No borre registros ni ejecute down-migrations para retirar la interfaz. Antes de promover, resuelva los bloqueos de `hallazgos_y_correcciones.md` y revise `07_auditoria_final.md`.
