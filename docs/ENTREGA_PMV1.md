# Entrega del backend PMV1

## Resultado

Backend PMV1 implementado y probado. Se conserva la arquitectura hexagonal original.
Esta entrega incluye el codigo, las pruebas, la documentacion y el SQL de referencia sin modificaciones.

## Verificaciones

- 45 pruebas aprobadas con pytest: casos de uso, validaciones, API, permisos, concurrencia e imports.
- Uvicorn: arranque real y HTTP 200 en /health, /docs y /openapi.json.
- compileall: correcto. pip check: sin conflictos.
- SQL intacto: SHA256 B4EE1A4376FD11F254FC9B3097BB7AE34D55182557CD792518B80E39D5E62C9A.
- Un aviso de Starlette sobre el uso de httpx en TestClient; ninguna prueba fallida.

## Arbol final de src/

M = archivo modificado; N = archivo nuevo; sin marca = conservado.

```text
src/
|-- adapters/
|   |-- in/
|   |   |-- controllers/
|   |   |   |-- .gitkeep
|   |   |   |-- catalogo_controller.py [N]
|   |   |   |-- ia_controller.py [M]
|   |   |   |-- informe_controller.py [N]
|   |   |   |-- solicitud_controller.py [M]
|   |   |   `-- usuario_controller.py [N]
|   |   `-- schemas/
|   |       |-- base.py [N]
|   |       |-- catalogo_response.py [N]
|   |       |-- error_response.py [N]
|   |       |-- informe_request.py [N]
|   |       |-- informe_response.py [N]
|   |       |-- prediccion_request.py [N]
|   |       |-- prediccion_response.py [N]
|   |       |-- solicitud_request.py [N]
|   |       `-- solicitud_response.py [N]
|   `-- out/
|       |-- ai/
|       |   |-- context_predictor_mock.py [N]
|       |   |-- generador_borrador_mock.py [N]
|       |   `-- ollama_adapter.py
|       `-- persistence/
|           |-- .gitkeep
|           |-- catalogo_repository_memory.py [N]
|           |-- datos_demo.py [N]
|           |-- informe_repository_memory.py [N]
|           |-- memoria.py [N]
|           |-- plantilla_repository_memory.py [N]
|           |-- prediccion_repository_memory.py [N]
|           `-- solicitud_repository_memory.py [M]
|-- application/
|   |-- ports/
|   |   |-- input/
|   |   |   |-- .gitkeep
|   |   |   `-- solicitud_use_case.py [M]
|   |   `-- output/
|   |       |-- .gitkeep
|   |       |-- catalogo_repository.py [N]
|   |       |-- context_predictor.py [N]
|   |       |-- generador_borrador.py [N]
|   |       |-- informe_repository.py [N]
|   |       |-- llm_port.py
|   |       |-- plantilla_repository.py [N]
|   |       |-- prediccion_repository.py [N]
|   |       |-- solicitud_repository.py [M]
|   |       `-- unidad_trabajo.py [N]
|   `-- use_cases/
|       |-- actualizar_borrador.py [N]
|       |-- actualizar_solicitud.py [N]
|       |-- consultar_catalogos.py [N]
|       |-- crear_solicitud.py [M]
|       |-- generar_borrador.py [M]
|       |-- guardar_valores_solicitud.py [N]
|       |-- obtener_informe.py [N]
|       |-- obtener_solicitud.py [M]
|       |-- predecir_contexto.py [N]
|       |-- servicios_solicitud.py [N]
|       `-- validar_prediccion.py [N]
|-- domain/
|   |-- entities/
|   |   |-- .gitkeep
|   |   |-- catalogo.py [N]
|   |   |-- informe.py [N]
|   |   |-- plantilla.py [N]
|   |   |-- prediccion_contexto.py [N]
|   |   |-- solicitud.py [M]
|   |   `-- usuario_actual.py [N]
|   |-- services/
|   |   |-- .gitkeep
|   |   |-- errores.py [N]
|   |   |-- informe_service.py [N]
|   |   `-- solicitud_service.py [M]
|   `-- value_objects/
|       |-- estado_solicitud.py [M]
|       `-- estados.py [N]
|-- infrastructure/
|   |-- auth/
|   |   `-- mock.py [N]
|   |-- configuration/
|   |   |-- .gitkeep
|   |   |-- container.py [N]
|   |   `-- settings.py [M]
|   `-- dependencies.py [N]
`-- main.py [M]
```

## Archivos creados

- `.gitignore`
- `docs/CONTRATOS_PMV1.md`
- `docs/ENTREGA_PMV1.md`
- `pytest.ini`
- `requirements.txt`
- `src/adapters/in/controllers/catalogo_controller.py`
- `src/adapters/in/controllers/informe_controller.py`
- `src/adapters/in/controllers/usuario_controller.py`
- `src/adapters/in/schemas/base.py`
- `src/adapters/in/schemas/catalogo_response.py`
- `src/adapters/in/schemas/error_response.py`
- `src/adapters/in/schemas/informe_request.py`
- `src/adapters/in/schemas/informe_response.py`
- `src/adapters/in/schemas/prediccion_request.py`
- `src/adapters/in/schemas/prediccion_response.py`
- `src/adapters/in/schemas/solicitud_request.py`
- `src/adapters/in/schemas/solicitud_response.py`
- `src/adapters/out/ai/context_predictor_mock.py`
- `src/adapters/out/ai/generador_borrador_mock.py`
- `src/adapters/out/persistence/catalogo_repository_memory.py`
- `src/adapters/out/persistence/datos_demo.py`
- `src/adapters/out/persistence/informe_repository_memory.py`
- `src/adapters/out/persistence/memoria.py`
- `src/adapters/out/persistence/plantilla_repository_memory.py`
- `src/adapters/out/persistence/prediccion_repository_memory.py`
- `src/application/ports/output/catalogo_repository.py`
- `src/application/ports/output/context_predictor.py`
- `src/application/ports/output/generador_borrador.py`
- `src/application/ports/output/informe_repository.py`
- `src/application/ports/output/plantilla_repository.py`
- `src/application/ports/output/prediccion_repository.py`
- `src/application/ports/output/unidad_trabajo.py`
- `src/application/use_cases/actualizar_borrador.py`
- `src/application/use_cases/actualizar_solicitud.py`
- `src/application/use_cases/consultar_catalogos.py`
- `src/application/use_cases/guardar_valores_solicitud.py`
- `src/application/use_cases/obtener_informe.py`
- `src/application/use_cases/predecir_contexto.py`
- `src/application/use_cases/servicios_solicitud.py`
- `src/application/use_cases/validar_prediccion.py`
- `src/domain/entities/catalogo.py`
- `src/domain/entities/informe.py`
- `src/domain/entities/plantilla.py`
- `src/domain/entities/prediccion_contexto.py`
- `src/domain/entities/usuario_actual.py`
- `src/domain/services/errores.py`
- `src/domain/services/informe_service.py`
- `src/domain/value_objects/estados.py`
- `src/infrastructure/auth/mock.py`
- `src/infrastructure/configuration/container.py`
- `src/infrastructure/dependencies.py`
- `tests/conftest.py`
- `tests/test_api.py`
- `tests/test_arquitectura.py`
- `tests/test_casos_uso.py`
- `tests/test_validaciones.py`

## Archivos modificados

- `README.md`
- `src/adapters/in/controllers/ia_controller.py`
- `src/adapters/in/controllers/solicitud_controller.py`
- `src/adapters/out/persistence/solicitud_repository_memory.py`
- `src/application/ports/input/solicitud_use_case.py`
- `src/application/ports/output/solicitud_repository.py`
- `src/application/use_cases/crear_solicitud.py`
- `src/application/use_cases/generar_borrador.py`
- `src/application/use_cases/obtener_solicitud.py`
- `src/domain/entities/solicitud.py`
- `src/domain/services/solicitud_service.py`
- `src/domain/value_objects/estado_solicitud.py`
- `src/infrastructure/configuration/settings.py`
- `src/main.py`

El SQL fue proporcionado por el usuario y no se cuenta como archivo creado por esta implementacion.

## Uso e integraciones pendientes

Los endpoints, comandos y la demo completa estan en [README](../README.md).
Las correspondencias SQL y firmas de integracion estan en [CONTRATOS_PMV1.md](CONTRATOS_PMV1.md).
Quedan a cargo del equipo: React, Supabase/PostgreSQL y su unidad de trabajo, Supabase Auth, RF-IA-01 y el adaptador LLM.
