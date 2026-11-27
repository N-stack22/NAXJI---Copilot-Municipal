# Prompt 3 — Dependencias backend

Main **4f4d294**, corte 27/11/2026. [pyproject.toml](../../../../pyproject.toml) es la declaración canónica; [requirements-runtime.lock.txt](../../../../requirements-runtime.lock.txt) fija la resolución runtime y [requirements-test.txt](../../../../requirements-test.txt) separa QA. `requirements.txt` delega al proyecto; no se altera ningún manifiesto en este cierre.

| Familia | Uso real | Fuente |
| ---| ---| ---|
| FastAPI, Pydantic, Uvicorn | Frontera HTTP, validación y servidor | [main](../../../../src/main.py), [controllers/schemas](../../../../src/adapters/in/) |
| psycopg[binary] | Parámetros, transacciones, bloqueos y JSONB | [postgres](../../../../src/adapters/out/persistence/postgres.py) |
| scikit-learn 1.6.1, joblib, numpy/scipy transitivas | Inferencia de modelos versionados; LogisticRegression y clasificador multietiqueta | [predictor](../../../../src/adapters/out/ai/sklearn_context_predictor.py), [integridad](../../../../src/adapters/out/ai/integridad_modelos.py) |
| httpx, python-dotenv | Transporte de proveedores y configuración del servidor | [Auth](../../../../src/infrastructure/auth/supabase.py), [O llama](../../../../src/adapters/out/ai/ollama_adapter.py), [database](../../../../src/infrastructure/configuration/database.py) |
| python-multipart, pypdf, python-docx, ReportLab, Pillow | Carga/extracción y representación Word/PDF | [documents](../../../../src/adapters/out/documents/) |

[SBOM Python](../../cierre-trazable/dependencias/sbom-python.json), [auditoría histórica](../../cierre-trazable/dependencias/python-audit-despues.json) y [CI de4f4d294](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611). No se repite pip-audit ni se presenta una auditoría antigua como garantía de ausencia actual de vulnerabilidades.

La instalación y build **Linux sí tienen evidencia** posterior: [Dockerfile](../../../../Dockerfile), [workflow Ubuntu](../../../../.github/workflows/ci.yml) y [recibo CI](../../understand/CI.md). La frase antigua «no se afirma ... Linux» corresponde al antecedente y queda superada. Los 46 SQL, joblib/JSON yDOCX se incluyen como package-data; las dependencias de herramientas no se confunden con archivos propios del conteo de Understand.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Dependencias backend

Entrada canónica `pyproject.toml`; `requirements.txt` instala el proyecto; archivo PMV2 delega al canónico. Resoluciones efectivamente instaladas en `requirements-runtime.lock.txt` y SBOM Python.

Críticas: FastAPI/Pydantic y contratos; psycopg y transacciones; sklearn/joblib/numpy/scipy para inferencia; httpx para proveedores; multipart/pypdf para carga y extracción; python-docx/ReportLab para exportación. Se corrigieron avisos del entorno candidato en certifi y Pillow. La consulta pip-audit posterior no reportó avisos conocidos. El wheel se importó en un venv nuevo fuera del repositorio; no se afirma haber validado instalación Linux.
