# GitHub Actions — entrega C-06

**Ejecución completa aprobada en main**, evento `push`, workflow «Calidad aislada»:
[46022681356](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46022681356).
Commit verificado: **b5842e4269dd3bf89c0a43e42708b0fe35ee588b**. Fecha de corte:27/11/2026, América/Lima.

| Validación | Resultado real |
|---|---|
| `pytest -q -ra` con PostgreSQL/pgvector aislado | **375 aprobadas,21 omitidas,1 advertencia** |
| `npm run test:frontend` | **55 aprobadas,0 fallidas,0 omitidas** |
| `npm run lint` | Aprobado |
| `npm run build` | Aprobado |
| `python -m build` | Wheel y sdist generados |
| Auditoría estática de dependencias y recursos SQL | 110 módulos,599 referencias import,16 adaptadores de persistencia,46 recursos;sin infracciones ni SQL fijo incrustado |
| Construcción Docker y verificación de recursos | Aprobado;imagen con usuario10001 y46 recursos SQL legibles |
| `git diff --check` | Aprobado;la comprobación local del diff preparado también terminó con exit0 |

Las **21 omitidas** siguen omitidas:10 requieren integración real Supabase/Auth y11 requieren Ollama/embeddings. Sus motivos literales están en el [extracto del job](ci-main-extracto.log). La advertencia corresponde a la deprecación de `starlette.testclient`/httpx; no es un fallo nuevo del producto. No se activaron servicios externos ni producción.

[Estado y pasos recibidos de GitHub](ci-main.json). El extracto conserva líneas originales con marca temporal UTC de Actions; la fecha de corte de este documento usa América/Lima. No es un log simulado ni una repetición atribuida al corte anterior. No se suman las27 pruebas locales de arquitectura/SQL a las375 de la suite integral, que ya las incluye.

Understand analizó las fuentes del padre **67d9db2f5591c1b08cb85cfe5f81dbd0ad311da9**; `b5842e4` añade solo documentación,evidencias,atributos para conservar archivos nativos y el exportador QA. Se comprobó diff vacío en las rutas del producto y las149 huellas de fuentes analizadas coinciden. El commit posterior que publica este recibo de CI conserva esas mismas fuentes; su ejecución de Actions puede consultarse en el [historial de main](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/workflows/ci.yml?query=branch%3Amain).
