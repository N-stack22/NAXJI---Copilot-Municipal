> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Dependencias backend

Entrada canónica `pyproject.toml`; `requirements.txt` instala el proyecto; archivo PMV2 delega al canónico. Resoluciones efectivamente instaladas en `requirements-runtime.lock.txt` y SBOM Python.

Críticas: FastAPI/Pydantic y contratos; psycopg y transacciones; sklearn/joblib/numpy/scipy para inferencia; httpx para proveedores; multipart/pypdf para carga y extracción; python-docx/ReportLab para exportación. Se corrigieron avisos del entorno candidato en certifi y Pillow. La consulta pip-audit posterior no reportó avisos conocidos. El wheel se importó en un venv nuevo fuera del repositorio; no se afirma haber validado instalación Linux.
