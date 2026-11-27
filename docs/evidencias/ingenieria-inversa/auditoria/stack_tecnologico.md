# Prompt 1 — Descubrimiento tecnológico vigente

Corte 27/11/2026, fuentes de main **4f4d294**. Los componentes se contrastan con código y manifiestos, sin reconstruir el stack desde alternativas de un informe. [Inventario verificable](../cierre-documental-20261127/inventario-fuente.json), [huellas](../cierre-documental-20261127/fuentes-sha256.json).

| Componente implementado | Archivos que lo acreditan | Alcance |
| ---| ---| ---|
| Python/FastAPI/Pydantic/Uvicorn | [pyproject.toml](../../../../pyproject.toml), [src/main.py](../../../../src/main.py) | Python >=3.11 declarado; Python 3.11 en Docker/CI. No se deduce una versión exacta instalada de una dependencia desde un rango del manifiesto. |
| React, JavaScript/JSX, Vite, Router, Axios | [package.json](../../../../package.json), [App.jsx](../../../../src/adapters/in/web/App.jsx), [vite.config.js](../../../../vite.config.js) | Aplicación JS/JSX; los paquetes `@types/react` no significan que la aplicación esté escrita en TypeScript. |
| PostgreSQL/pgvector y psycopg | [postgres.py](../../../../src/adapters/out/persistence/postgres.py), [buscar.sql](../../../../src/adapters/out/persistence/sql/documentos_postgres/buscar.sql), [migración RAG](../../../../database/migrations/20261030_01_documentos_rag.sql) | SQL fijo en recursos y vector(1024); parámetros e identificadores seguros en Python. |
| Supabase Auth/Storage | [supabase.py](../../../../src/infrastructure/auth/supabase.py), [almacen_supabase.py](../../../../src/adapters/out/documents/almacen_supabase.py) | Integración REST del backend; PostgreSQL se accede mediante psycopg. No de muestra disponibilidad de un proyecto Supabase destino. |
| scikit-learn 1.6.1, LogisticRegression | [SklearnContextPredictor](../../../../src/adapters/out/ai/sklearn_context_predictor.py), [modelo configurado](../../../../src/infrastructure/ai/models/model_config.json), [procedencia/replay](../../cierre-trazable/ml/procedencia-particiones-replay.json) | Predicción de tipo/área y OneVsRestClassifier[LogisticRegression] de temas normativos. RF-IA-01 es un identificador histórico, no RandomForest. No se reentrena ni cambia artefactos. |
| O llama qwen2.5:7b y embeddings bge-m3:567m | [Settings](../../../../src/infrastructure/configuration/settings.py), [RagSettings](../../../../src/infrastructure/configuration/rag.py), [adaptadores IA](../../../../src/adapters/out/ai/) | Defaults configurables; embeddings 1024. [Evidencia RAG real histórica](../../cierre-trazable/rag-embeddings-reales.json), separada de pruebas con dobles. |
| DOCX/PDF y extracción | [exportadores/extractor](../../../../src/adapters/out/documents/), [empaquetado](../../../../pyproject.toml) | python-docx, ReportLab, pypdf; no OCR integrado para cualquier PDF escaneado. |
| Herramientas QA | [CI](../../../../.github/workflows/ci.yml), [ZAP](../../cierre-seguridad-20261126/zap/despues/ejecucion.json), [Understand](../../understand/README.md) | pytest, Node/JSDOM, ESLint, build, Docker, ZAP 2.17.0 y Understand 8.1.1269 ejecutados con sus cortes/alcances. |

**Alternativas evaluadas, no implementadas:** Qdrant, TypeScript y arquitectura Event-Driven con broker/workers. La auditoría SQL de eventos y las reservas síncronas no transforman el backend en Event-Driven. No se migra el producto para acomodar una alternativa documental.

[Inventario de archivos](inventario_archivos.md), [dependencias](../dependencias/backend.md) y [consolidado](../../../ingenieria_inversa.md). Las versiones resueltas están en los locks; las auditorías/SBOM son fotografías históricas, no una consulta de vulnerabilidades actualizada hoy.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Descubrimiento tecnológico

Confianza alta por imports, manifiestos y ejecución: Python 3.11/FastAPI/Pydantic/Uvicorn, React/JSX/Router/Vite/Axios, psycopg/PostgreSQL/pgvector, sklearn/joblib, Ollama, python-docx/pypdf/ReportLab. Auth y Storage son adaptadores REST Supabase; su despliegue no se certificó.

No se encontró TypeScript, Qdrant, aplicación móvil o reconocimiento de imágenes en el producto. El predictor existente es LogisticRegression y OneVsRestClassifier[LogisticRegression]; RF-IA-01 es el identificador histórico del requerimiento. Locks y SBOM documentan versiones, no se deducen del nombre del proyecto.
