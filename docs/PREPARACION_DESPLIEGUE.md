# Preparación de despliegue: Railway y Cloudflare Pages

Se entrega configuración y artefactos de despliegue. **No se despliega ni se cambian servicios, secretos o Supabase compartido.** Los 3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario. La preparación técnica no acredita que las credenciales o servicios externos estén configurados.

## Backend

`Dockerfile` usa Python 3.11 con digest fijado, dependencias de `requirements-runtime.lock.txt`, wheel instalado sin red en la etapa final, usuario `10001`, contexto limitado por `.dockerignore` y sin archivos `.env`. Las dependencias se cachean en una capa anterior al código; timeout y reintentos de PyPI son explícitos. El primer build local de release tuvo un timeout real de descarga; su log se conserva. Consultar el resultado del reintento y de CI en `RESULTADOS_CIERRE.md`.

```powershell
docker build -t naxji-backend:release .
# En un entorno con variables privadas ya cargadas; muestra nombres de errores, nunca valores:
python deploy/preflight.py
```

En Railway seleccionar esta rama/commit revisado, raíz del repositorio y Dockerfile. `railway.toml` declara healthcheck `/health` y reinicio ante fallo. El arranque valida `PORT` y escucha en `0.0.0.0`; no ejecuta migraciones ni semillas. `/health` es liveness: no demuestra conectividad a PostgreSQL/Ollama. `/ready` conserva autorización administrativa y puede usarse en una comprobación operativa posterior.

Configurar en las variables privadas del servicio:

| Grupo | Variables / criterio |
|---|---|
| Modo | `NAXJI_PERSISTENCE_MODE=postgres`, `NAXJI_AUTH_MODE=supabase` |
| PostgreSQL | `NAXJI_DB_HOST`, `PORT`, `NAME`, `USER`, `PASSWORD`, `SSLMODE` — todos con prefijo `NAXJI_DB_`; SSL `require`, `verify-ca` o `verify-full` |
| Supabase Auth | `NAXJI_SUPABASE_URL`, `NAXJI_SUPABASE_PUBLISHABLE_KEY`; publicable/anon, nunca service_role en frontend |
| Cookies HTTPS | `NAXJI_AUTH_COOKIE_SECURE=true`; para los sitios distintos Pages/Railway, `NAXJI_AUTH_COOKIE_SAMESITE=none`; conservar protección de origen/cabecera y considerar las restricciones de cookies de terceros |
| Orígenes | `NAXJI_CORS_ORIGINS=https://naxji.pages.dev` y `NAXJI_AUTH_ALLOWED_ORIGINS=https://naxji.pages.dev`; ajustar si cambia el dominio, sin comodines |
| Ollama | `NAXJI_OLLAMA_BASE_URL` a servicio privado estable alcanzable desde Railway; modelo `qwen2.5:7b`, embedding `bge-m3:567m`; no `localhost` ni túnel ngrok como solución de producción |
| PMV2 | `NAXJI_RAG_ENABLED=true` solo con esquema/bucket ya preparados; `NAXJI_STORAGE_BUCKET`, `NAXJI_STORAGE_SERVICE_KEY` privados; dimension1024 y política actual sin cambios |
| PMV3 | `NAXJI_PMV3_ENABLED=true` solo con migración de eventos ya aplicada al entorno correspondiente |
| API | `NAXJI_API_DOCS_ENABLED=false` para el servicio publicado; el laboratorio de ZAP habilita OpenAPI de forma explícita |
| Proxy | `FORWARDED_ALLOW_IPS` según los proxies de confianza de la infraestructura; no se habilita confianza universal por defecto |

No pegar secretos en commits, capturas, tickets ni variables `VITE_*`. El preflight es **offline**: verifica forma/configuración, no autentica ni conecta. En esta entrega no se usaron credenciales de despliegue; no se certifica su validez.

## Base de datos y activación

Conservar el esquema y las migraciones existentes. El operador debe comprobar cuáles ya están aplicadas antes de ejecutar nada. No repetir `NAXJI_database_schema_actual.sql` contra una base poblada. La migración PMV3 `database/migrations/20261126_01_pmv3_revision.sql` es la adición histórica; esta rama no la cambia ni crea otra. Las semillas de pilotos siguen siendo optativas y no se alteran. Nunca borrar eventos/versiones para hacer rollback; desactivar la bandera de la función o volver a una imagen compatible manteniendo los datos.

## Frontend

El dominio informado es Cloudflare Pages (`naxji.pages.dev`). Configurar Node24, build `npm ci && npm run build`, salida `dist` y **solo** la variable pública `VITE_API_URL=https://naxji-production.up.railway.app` (sin `/docs`). Para otro backend, cambiar también `connect-src` de `public/_headers` a ese origen exacto antes de compilar. La API no necesita Supabase keys en el navegador.

`public/_headers` se copia a `dist/_headers`. Define CSP sin scripts inline/eval, protección de marcos, `nosniff`, política de referentes y permisos. La política preserva las hojas CSS externas y la asignación de propiedades de estilo por React; no se modificó JSX ni pilotos. El escaneo local emula ese archivo sobre el build real; no es una comprobación del edge de Cloudflare. Para GitHub Pages esos headers no se aplican automáticamente: usar un proxy con cabeceras o el hosting Pages informado.

Los paquetes Python salen a `build/backend` o un directorio separado con `python -m build --outdir build/backend`; no publicar wheels/tar.gz junto con los recursos web de `dist`.

## Promoción y reversión

1. Revisar commit, resultados locales/CI, imagen/paquete y variables sin exponer valores.
2. Preparar servicios y comprobar estado de migraciones con el operador; esta entrega no ejecuta esos pasos externos.
3. Desplegar la imagen seleccionada; comprobar `/health` y, con identidad administrativa autorizada, `/ready`.
4. Verificar sesión y CORS desde el dominio publicado, biblioteca, revisión e importación de una fuente autorizada. No presentar esta lista manual como pruebas realizadas.
5. Ante fallo, restaurar imagen/configuración anterior compatible; preservar eventos y versiones. No introducir migraciones destructivas.

Fuentes: [Railway FastAPI](https://railway.com/guides/fastapi), [healthchecks/PORT](https://docs.railway.com/deployments/healthchecks), [Cloudflare `_headers`](https://developers.cloudflare.com/pages/configuration/headers/), [CSP de estilos](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src-attr).
