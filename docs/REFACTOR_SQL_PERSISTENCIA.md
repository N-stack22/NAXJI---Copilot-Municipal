# Consultas SQL como recursos de persistencia

Refactor del 13/11/2026, a partir de `main` (`96396cd`). No modifica el esquema, las migraciones, los puertos ni los casos de uso.

Las consultas fijas de los tres adaptadores se encuentran en `src/adapters/out/persistence/sql/`:

| Adaptador | Directorio | Recursos |
|---|---|---:|
| `DocumentosPostgres` | `documentos_postgres/` | 14 |
| Unidad de trabajo y repositorios PMV1 | `postgres/` | 25 |
| `PerfilRepositoryPostgres` | `perfil_repository_postgres/` | 2 |
| Total | | 41 |

`sql_resources.consulta()` utiliza `importlib.resources` y una caché de lectura. Funciona independientemente del directorio de ejecución. Los nombres de recursos son constantes internas. Python conserva los parámetros de `execute()`, transacciones, validaciones y mapeos de filas a entidades.

`save()` conserva `psycopg.sql.Identifier`, `Placeholder`, `SQL.format()` y `SQL.join()`. Sus plantillas de INSERT/UPSERT/asignación se cargan de recursos; ningún valor de negocio se interpola en el texto SQL. `bloquear.sql` es un fragmento interno que se agrega únicamente cuando la unidad de trabajo está activa. Esos cuatro recursos son plantillas/fragmentos, no consultas independientes para ejecutar desde el editor SQL.

## Comportamiento conservado

- Deduplicación documental con `pg_advisory_xact_lock` y comparación nula segura del área.
- Reserva y finalización con `SELECT ... FOR UPDATE`, comprobación del intento y vencimiento.
- Eliminación de fragmentos anteriores, inserciones y actualización del estado en la misma transacción. Un fallo de inserción revierte todas esas escrituras.
- Búsqueda exacta coseno con pgvector: la CTE `autorizados AS MATERIALIZED` filtra propietario, administrador, ámbito institucional/área, estado y revisión de procesamiento antes de ordenar/limitar. Se conserva el desempate por ID y el umbral.
- Resolución de pgvector en `public` o `extensions`, sin cambiar el esquema donde está instalada la extensión.
- Lecturas consistentes de PMV1, bloqueo condicional dentro de la unidad de trabajo, snapshots y citas por versión, selección de roles activos conocidos.

## Empaquetado

`pyproject.toml` declara el backend como paquete de Python, con descubrimiento de namespaces y recursos de paquete para los `.sql`. También incluye los modelos sklearn/JSON y la plantilla DOCX existentes, necesarios para que el backend instalado funcione. `MANIFEST.in` incluye esos recursos en el sdist. Las dependencias de ejecución corresponden a las empleadas actualmente por PMV1/PMV2.

Construcción reproducible, desde un checkout limpio y sin ejecutarla a la vez que pytest:

```powershell
python -m pip install build wheel "setuptools>=77"
python -m build --no-isolation
```

El wheel y el sdist deben contener los 41 recursos bajo `src/adapters/out/persistence/sql/`. La verificación de entrega comprueba sus bytes frente al código fuente y carga todas las consultas desde el wheel extraído, con Python aislado y fuera del checkout. Además importa `src.main` desde ese paquete, con configuración de memoria y sin servicios externos, comprobando que se incluyen sus modelos y plantilla Word.

## Pruebas

Entorno local desechable: contenedor `pgvector/pgvector:pg18`, PostgreSQL 18.6, pgvector 0.8.7, puerto exclusivamente loopback `127.0.0.1:55434`. Cada fixture crea una base aleatoria y elimina únicamente esa base al terminar. No se utiliza `.env`, Supabase compartido ni producción. Auth/Storage y generación se prueban con los dobles explícitos existentes; la persistencia y las operaciones vectoriales son reales.

```powershell
$env:NAXJI_TEST_PG_PORT = "55434"
python -m pytest -q -rs tests
```

Resultado: **301 aprobadas, 21 omitidas**. Incluye:

- Las dos pruebas existentes de arquitectura y las dos nuevas sobre separación de SQL y carga de todos los recursos fuera del checkout.
- Pruebas existentes de persistencia PMV1: estructura, generación concurrente, correspondencias, compatibilidad histórica, plantillas y versiones/Word.
- Pruebas existentes de PMV2 con PostgreSQL/pgvector, permisos, reservas, citas y extensión instalada en `extensions`.
- Tres regresiones nuevas sobre rollback tras una segunda inserción inválida, bloqueo/visibilidad atómica y permisos antes de `top_k`, y una prueba real del adaptador de perfiles/roles.

Las 21 omisiones: 10 integraciones remotas Supabase/Auth, 9 de Ollama real y 2 de PMV2 con embeddings/Ollama reales. Los motivos y casos concretos aparecen con `-rs`. No se omiten las pruebas de persistencia local habilitadas por `NAXJI_TEST_PG_PORT`.

Se conserva una advertencia del entorno: deprecación de Starlette/httpx en `fastapi.testclient`. No corresponde a un fallo del refactor.
