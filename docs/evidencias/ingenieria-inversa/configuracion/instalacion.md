# Prompt 4 — Reconstrucción del entorno

Main **4f4d294**, corte 27/11/2026. [Dockerfile](../../../../Dockerfile), [pyproject.toml](../../../../pyproject.toml), [package.json](../../../../package.json) y [CI](../../../../.github/workflows/ci.yml) son las fuentes de los requisitos. Python>=3.11; Docker usa 3.11-slim fijado por digest yCI Ubuntu usaPython 3.11/Node 24. No se copia un venv de Windows a Linux.

Instalación local en un checkout limpio con entorno propio: crear venv e instalar el lock runtime y requirements de pruebas; `npm ci` para frontend. Arranque y variables por proceso en [GUIA_CIERRE_Y_DEMO](../../../GUIA_CIERRE_Y_DEMO.md), detalles de entrega en [PREPARACION_DESPLIEGUE](../../../PREPARACION_DESPLIEGUE.md). Esta revisión no ejecuta instaladores ni sobrescribe `.env`.

| Recorrido registrado | Evidencia |
| ---| ---|
| Wheel/sdist e importación fuera del árbol, Windows | [empaquetado histórico](../../cierre-trazable/empaquetado/); SQL, modelos yDOCX son package-data. |
| Linux/Ubuntu, pytest, frontend, build y paquete | [CI 4 f 4 d 294](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611), [workflow](../../../../.github/workflows/ci.yml). No son solo comandos sugeridos. |
| Imagen runtime sin secretos | [Dockerfile](../../../../Dockerfile): usuario 10001, PORT configurable, healthcheck; [resultado del cierre](../../../RESULTADOS_CIERRE.md). |
| PG/pgvector desechable | Servicio de integración y fixtures de bases aleatorias; sin tocar el esquema compartido. |

Las migraciones son archivos versionados de aplicación manual autorizada; el arranque no las aplica silenciosamente. RAG yPMV 3 tienen banderas y prerrequisitos documentados; su valor de fábrica false no significa que lasHU estén sin implementar. El preflight valida configuración offline, no credenciales ni disponibilidad real.

[Servicios](servicios.md), [precedencia y variables](variables_entorno.md). El antecedente que solo tenía guía Ubuntu conserva su fecha lógica y no invalida la ejecución Linux posterior.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Reconstrucción del entorno

Requisitos verificados: Python 3.11, Node/npm, Docker para integración aislada y Ollama para pruebas reales. Consulte `../../../GUIA_CIERRE_Y_DEMO.md` para comandos PowerShell/Ubuntu y activación por proceso.

Prueba efectuada: build de wheel/sdist, instalación runtime en venv nuevo desde lock, instalación de wheel e importación con `-I` fuera del árbol. Se verificaron 46 recursos SQL, modelos y DOCX. El lock fue obtenido en Windows; los comandos Ubuntu son una guía preparada, no una ejecución registrada. No copie venv entre plataformas ni sustituya `.env` privados.
