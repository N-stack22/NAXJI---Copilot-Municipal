# NAXJI — Copilot Municipal: backend PMV1

API FastAPI con arquitectura hexagonal, persistencia en memoria y adaptadores de IA **mock**.
Permite crear una solicitud, confirmar/corregir contexto, completar una plantilla,
generar un borrador y guardar ediciones como versiones. El SQL proporcionado se usa
como referencia y no se ejecuta ni modifica.

## Ejecutar en Windows / PowerShell

Requiere Python 3.11 o superior. Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

- Salud: http://127.0.0.1:8000/health
- Swagger: http://127.0.0.1:8000/docs
- OpenAPI: http://127.0.0.1:8000/openapi.json

Use **un solo proceso/worker** en la demo: cada proceso tiene memoria independiente.
Reiniciar o recargar el servidor elimina solicitudes, predicciones e informes.

## Usuario temporal y roles

En Swagger pulse **Authorize** e introduzca `demo-funcionario` (sin escribir `Bearer`).
En Postman use `Authorization: Bearer demo-funcionario`.

| Token ficticio | Comportamiento de prueba |
|---|---|
| `demo-funcionario` | Crear, consultar y editar sus propias solicitudes e informes |
| `demo-otro` | Otro propietario; no puede acceder a los recursos del primero |
| `demo-revisor` | Identidad del primer usuario con rol de lectura; no puede elaborar |
| `demo-aprobador` | Identidad del primer usuario con rol de lectura; no puede elaborar |
| `demo-admin` | Elaborar y acceder a todos los recursos de la demo |

Estos valores son selectores de identidades ficticias, **no credenciales ni sesiones reales**.
No se crean usuarios ni se almacenan contraseñas. Inicio, cierre de sesión y validación
de JWT corresponden a Supabase Auth y quedan pendientes. El futuro adaptador deberá
reemplazar `get_current_user` y resolver perfiles/roles verificados.

Configuración opcional antes de iniciar el servidor:

```powershell
$env:NAXJI_AUTH_MODE = "mock"
$env:NAXJI_CORS_ORIGINS = "http://localhost:5173"
```

`NAXJI_AUTH_MODE=disabled` rechaza todos los tokens en rutas protegidas;
`/health`, `/docs` y `/openapi.json` permanecen públicos. La política de autorización
de la demo está en `autorizar`; debe acordarse con el equipo antes de producción.
CORS queda cerrado salvo los orígenes configurados.

## Demo completa en Swagger / Postman

1. Consulte `GET /tipos-informe` y `GET /areas`. Los cuatro códigos de tipo provienen
   del SQL; UUID, áreas, plantillas y normativa son fixtures ficticias.
2. Cree `POST /solicitudes` con `{"asunto":"Inspección de un parque"}`.
   Guarde el `id` devuelto. Puede incluir tipo, áreas y plantilla desde este paso.
3. Consulte y edite mediante `GET /solicitudes/{id}` y `PUT /solicitudes/{id}`.
   El PUT actualiza solo los campos enviados; las referencias admiten `null`.
4. Ejecute `POST /solicitudes/{id}/predecir-contexto`, sin cuerpo.
   La respuesta identifica `es_mock: true`, el modelo ficticio y las confianzas de prueba.
5. Confirme con `POST /solicitudes/{id}/validar-prediccion`:

   ```json
   {"prediccion_id":"UUID_DEVUELTO", "resultado":"ACEPTADA"}
   ```

   Para corregir, envíe `resultado: "CORREGIDA"`, `tipo_informe_id`,
   `area_destino_id` y opcionalmente `normativa_ids` con las normativas predichas
   que conserva. `[]` descarta todas. `RECHAZADA` impide generar.
   Solo se valida la predicción más reciente. La respuesta conserva la propuesta
   original; `GET /solicitudes/{id}` muestra el tipo/área finalmente confirmados.
6. Consulte `GET /plantillas?tipo_informe_id=UUID_CONFIRMADO`.
   Seleccione una con `PUT /solicitudes/{id}` y `{"plantilla_id":"UUID_PLANTILLA"}`.
   Si seleccionó una plantilla antes de predecir, el contexto confirmado debe
   coincidir con su tipo; de lo contrario quite/cambie la plantilla o corrija el contexto.
7. Consulte `GET /plantillas/{plantilla_id}/campos` y copie los IDs de los campos
   `antecedentes` y `detalle`. Guarde:

   ```json
   {
     "valores": [
       {"campo_plantilla_id":"UUID_ANTECEDENTES", "valor":"Solicitud de inspección recibida."},
       {"campo_plantilla_id":"UUID_DETALLE", "valor":"Se registraron observaciones en el parque."}
     ]
   }
   ```

   Use `PUT /solicitudes/{id}/valores`. **Reemplaza todo el conjunto de valores**;
   incluya también los que desea conservar. Puede guardar formularios incompletos,
   pero no generar con ellos. Los tipos admitidos son text, textarea, date
   (`YYYY-MM-DD`), number, boolean y select. Los campos select de la demo usan
   `configuracion.opciones`; es una convención del mock, no una restricción nueva del SQL.
8. Ejecute `POST /solicitudes/{id}/generar-borrador` con
   `{"instrucciones":"Respetar los datos de la inspección."}` o `{}`.
   Recibirá `informe_id`, `estado: BORRADOR`, `numero_version: 1` y `contenido`.
   El mock devuelve texto de demostración, sin realizar inferencia ni llamadas externas.
9. Recupere `GET /informes/{informe_id}` y edite con `PUT /informes/{informe_id}`:

   ```json
   {
     "numero_version": 1,
     "contenido": {
       "antecedentes": "Solicitud de inspección recibida.",
       "desarrollo": "Contenido revisado por el funcionario.",
       "conclusiones": "Conclusiones editadas."
     }
   }
   ```

   Se agrega la versión 2, con origen `USUARIO`; la versión anterior se conserva.
   Envíe la versión que leyó. Una versión antigua produce 409.

Los IDs ilustrativos `UUID_...` deben reemplazarse por UUID reales devueltos por la API.
El flujo anterior también se verifica automáticamente en `tests/test_api.py`.

## Endpoints

| Método | Ruta | Uso |
|---|---|---|
| GET | `/health` | Estado, sin autenticación |
| GET | `/auth/me` | Identidad temporal actual |
| POST | `/solicitudes` | Crear; devuelve 201 |
| GET | `/solicitudes/{solicitud_id}` | Consultar |
| PUT | `/solicitudes/{solicitud_id}` | Modificar campos o cancelar |
| PUT | `/solicitudes/{solicitud_id}/valores` | Guardar valores de plantilla |
| GET | `/tipos-informe` | Catálogo de tipos |
| GET | `/areas` | Catálogo de áreas |
| GET | `/plantillas` | Plantillas activas; filtro opcional por tipo |
| GET | `/plantillas/{plantilla_id}/campos` | Campos activos ordenados |
| POST | `/solicitudes/{solicitud_id}/predecir-contexto` | Predicción mock |
| POST | `/solicitudes/{solicitud_id}/validar-prediccion` | Confirmar/corregir/rechazar |
| POST | `/solicitudes/{solicitud_id}/generar-borrador` | Generar mock; devuelve 201 |
| GET | `/informes/{informe_id}` | Consultar la última versión |
| PUT | `/informes/{informe_id}` | Guardar una nueva versión |

Se conserva `POST /solicitudes/` como alias. El cuerpo anterior `descripcion`
se sustituye por valores de plantilla, porque no existe esa columna en `solicitudes`.
Los IDs enteros anteriores se sustituyen por UUID.

Estados de solicitud: `BORRADOR → LISTA_PARA_GENERAR → PROCESANDO → GENERADA`.
Los dos primeros admiten cancelación a `CANCELADA`. La API deriva los estados;
solo acepta `CANCELADA` como cambio manual. Modificar asunto/tipo/destino invalida
la confirmación; cambiar plantilla elimina valores de la plantilla anterior.
Cambiar el asunto exige una nueva predicción. Cada solicitud puede generar un único informe.
PMV1 solo edita informes en `BORRADOR`; los demás estados del SQL están definidos,
pero sus flujos de revisión/aprobación quedan fuera de este alcance.

Errores: 400 reglas/datos de negocio, 401 sin autenticación, 403 permiso/propietario,
404 recurso inexistente, 409 estado/versión incompatible, 422 request inválido y
500 fallo interno o de generación. Los errores 500 no exponen detalles del proveedor.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src tests
.\.venv\Scripts\python.exe -m pip check
```

Se cubren casos de uso, validaciones, contratos mock, control por rol/propietario,
concurrencia de generación, rollback, versiones, endpoints, Swagger, CORS e imports.
`httpx` se utiliza en TestClient; no se realizan llamadas a servicios externos en las pruebas.
Con las versiones instaladas, Starlette emite un aviso de deprecación de su uso de
httpx en TestClient; las pruebas pasan. No se añadió otro cliente HTTP por ese aviso.

## Integración pendiente y contratos

Consulte [docs/CONTRATOS_PMV1.md](docs/CONTRATOS_PMV1.md) y el
[inventario de entrega](docs/ENTREGA_PMV1.md).

- Frontend React: consumir OpenAPI, catálogos, solicitudes, contexto y edición de informes.
- Base de datos: implementar los repositorios y la unidad de trabajo con Supabase/PostgreSQL.
- Auth: sustituir la dependencia temporal por verificación de Supabase Auth y lectura de perfil/roles.
- RF-IA-01: implementar `ContextPredictor`, con IDs de catálogos reales y confianzas.
- LLM: implementar `GeneradorBorrador` con plantilla, datos, contexto e instrucciones.

El `OllamaAdapter` y `LLMPort` que ya existían en el commit remoto se conservan sin
modificaciones. No se importan ni instancian al iniciar la aplicación PMV1. Su contrato
antiguo de texto/prompt requerirá adaptación por el responsable de la integración;
el controller PMV1 utiliza exclusivamente el puerto estructurado y su mock.

## Frontend PMV 1

El Front-End de PMV 1 está en la carpeta [`frontend`](frontend). No modifica la API.

```powershell
cd frontend
npm install
npm run dev
```

Consume este backend en `http://127.0.0.1:8000`. Detalle de instalación: [frontend/README.md](frontend/README.md).
