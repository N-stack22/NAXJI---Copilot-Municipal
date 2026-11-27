# Inventario vigente de fuentes y recursos

Lectura estática de archivos versionados en main **4f4d294**, corte 27/11/2026. [Inventario fuente](../cierre-documental-20261127/inventario-fuente.json):110 módulos Python en `src` (dominio 18, aplicación 31, adaptadores 52, infraestructura 8 ymain 1). Se separan los dos Python de `deploy` y los 37 archivos Web:149 archivos propios del alcance de Understand. Estos conteos no incluyen tests, bibliotecas ni archivos generados.

[Huellas actuales](../cierre-documental-20261127/fuentes-sha256.json) coinciden exactamente con las 149 [huellas del análisis Understand](../../understand/fuentes-sha256.json). No se vuelve a ejecutar Understand ni se recalculan sus métricas. El inventario AST identifica clases, campos, métodos y líneas; no se confunde con las 141 clases/696 funciones globales de Understand, que aplican sus propias reglas.

| Ubicación | Contenido observado |
| ---| ---|
| [src/domain](../../../../src/domain/) | Dataclasses, enumeraciones y políticas; [dominio](../analisis/dominio.md). |
| [src/application](../../../../src/application/) | Puertos, DTO, orquestación y autorización por casos de uso. |
| [src/adapters](../../../../src/adapters/) | API/React y salidas PG/memoria, IA, documentos/exportación. |
| [src/infrastructure](../../../../src/infrastructure/) | Configuración, composición, Auth y artefactos ML. |
| [database](../../../../database/) | Migraciones, checks y semillas versionados; no se ejecutan en este cierre. |
| [sql](../../../../src/adapters/out/persistence/sql/) | 46 recursos fijos por adaptador, empaquetados por `pyproject.toml`. |
| [models](../../../../src/infrastructure/ai/models/), [templates](../../../../src/adapters/out/documents/templates/) | Cinco joblib, JSON de configuración y plantillas DOCX; intactos. |
| [deploy](../../../../deploy/), [Dockerfile](../../../../Dockerfile), [workflow](../../../../.github/workflows/ci.yml) | Arranque/preflight offline, imagen reproducible y validaciones Linux. |

`.env`, dependencias instaladas,`node_modules`, venv, dist y originales académicos no se extraen ni se publican como evidencia de configuración. El [inventario histórico](../../cierre-trazable/ingenieria-inversa/inventario.json) se conserva; no se lo presenta como un escaneo nuevo.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Inventario de archivos

Escaneo local de `src`: dominio 18 archivos Python; aplicación 31; adaptadores 52; infraestructura 8 al corte de esta reconstrucción. El detalle de clases, rutas y conteos está en `../../cierre-trazable/ingenieria-inversa/inventario.json`.

Los archivos Python/JSX/JS/CSS implementan el producto. SQL fijo se distribuye en 46 recursos por adaptador; migraciones y semillas se conservan en `database/`. Se empaquetan cinco joblib, configuración del modelo y DOCX base. `.env`, venv, node_modules, build y originales académicos no forman parte del paquete. El inventario se obtiene de archivos/AST/OpenAPI, no de nombres de tecnologías en el informe.
