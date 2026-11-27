# Resultados del cierre académico y preparación de despliegue

## Actualización C-06 — 27/11/2026

**Understand ejecutado, C-06 cerrada.** Último main analizado **67d9db2f5591c1b08cb85cfe5f81dbd0ad311da9**, herramienta8.1.1269 instalada/licenciada en Windows. [Evidencias completas](evidencias/understand/README.md):149 archivos propios (112Python/37Web),6.719 líneas de código,141 clases,696 funciones,complejidad máxima26;SonargraphMaintainability84,44774960712785. Halstead original se entrega por archivo/función; no existe valor global disponible. CSV,7 reportes HTML con sus tablas/gráficos disponibles,SVG/PNG nativos y XML de arquitectura.423 relaciones propias resueltas;0 infracciones de las reglas dominio/aplicación.0 errores y224 advertencias de resolución explicadas.

No se confirma un defecto funcional que justifique cambiar código de producto. Solo se añaden evidencia, exportador reproducible e informes; no se toca PMV,plantillas,ML,RAG,esquema,`.env`,Supabase ni informe académico final. **27 pruebas de arquitectura/SQL aprobadas,0 omitidas** en la comprobación complementaria; [log](evidencias/understand/pruebas-arquitectura-sql.log). La ejecución integral de GitHub Actions de esta entrega se enlaza desde el índice de evidencias una vez comprobada. Las375/21 y55 de abajo son resultados del corte anterior, no pruebas nuevas de esta sesión. No se repite carga750 porque no cambia rendimiento ni producto.

Las referencias a Understand bloqueado del anexo histórico se conservan como estado de aquel corte; quedan superadas por esta ejecución. La validación institucional y de servicios externos sigue fuera del alcance; ninguna omitida pasa a aprobada.

## Corte anterior: seguridad y preparación de despliegue

Corte:26/11/2026, América/Lima. Base `main` **7359a67**; rama **feature/cierre-seguridad-despliegue**. Los **3 PMV y 10 HU se aceptan para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Esta aceptación no transforma omitidas en aprobadas ni autoriza afirmar resultados no medidos.

## Cambios y componentes conservados

Se refuerzan `tests/test_arquitectura.py` y `tests/test_sql_resources.py`: imports relativos/alias/dinámicos literales, dominio→aplicación, recorrido completo y descubrimiento recursivo de persistencia, SQL concatenado/f-strings/comentarios. Se revisan **110 módulos y 599 referencias import**, **16 módulos de persistencia y 46 recursos SQL**, sin infracciones confirmadas. Por ello no se modifican los adaptadores ni la composición segura de `save()`.

ZAP confirmó ausencias de cabeceras. Solo se añade `nosniff` a respuestas de API/incluido 500 y `public/_headers` para CSP, marcos y `nosniff` del hosting estático. **No hay diff frente a7359a67 en dominio, aplicación, pilotos, modelos, predictor, RAG, persistencia, esquema, semillas ni JSX/advertencias HU-IA-04.** No se toca el informe académico final ni `.env`.

## Pruebas actuales y omitidas

| Control | Resultado | Evidencia |
|---|---|---|
| Línea base7359a67 |346 backend aprobadas/21 omitidas; 55 frontend; lint/build/diff0|`evidencias/cierre-seguridad-20261126/linea-base/`|
| Suite tras correcciones |**375 aprobadas,21 omitidas,0 fallidas**,1 deprecación de QA|`verificacion-final-02/` (d5edbc2,38,29s); corrida 01 conservada|
| Frontend |**55 aprobadas,0 omitidas/0 fallidas**|`frontend.txt`|
| npm lint / npm build / git diff --check |Exit0|Logs de verificación|
| python -m build |Wheel y sdist construidos|`empaquetado/python-build.log`; salida separada de dist web|
| Docker release local |Primer intento falló por timeout PyPI; reintento**exit0**,47,70s|Ambos logs y JSON de empaquetado conservados|
| Smoke de imagen, red none |UID 10001, read-only, PORT 8088,/health200, nosniff,/docs404,46SQL, predictor/PDF cargados|`empaquetado/smoke-imagen/resultado.json`; sin credenciales externas|
| Arranque productivo sin configuración |Exit1 **esperado**, sin caída a memoria|`arranque-sin-config.log`; no se cuenta como una prueba fallida de aplicación|
| CI Linux real |Ejecución 45939307152 **success**, commit d5edbc2|[GitHub Actions](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/45939307152); logs y pasos en `ci/`|

Las **21 omitidas** son 10 integraciones Supabase (1 Auth,3 catálogos,6 generales) y 11 integraciones reales de Ollama/embeddings opt-in. No se ejecutan en esta misión. La evidencia histórica de otras corridas IA se conserva separada y no se atribuye a esta suite. La advertencia Starlette/TestClient/httpx está en el log; no se oculta.

CI e4f4ecf pasó375/21 y 55 frontend, pero falló al comparar contra7359a67 porque checkout solo traía un commit. Se corrigió con fetch-depth0; no se relajó la auditoría. Logs del fallo y ejecuciones exitosas posteriores están archivados. Los ERROR de PostgreSQL dentro de fixtures de rollback/inmutabilidad son fallos provocados esperados, distintos de la conclusión del job.

## ZAP real, antes/después

Imagen oficial ZAP **2.17.0**, digest `9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af`. Objetivos fijos `http://naxji-api:8001/` y `http://naxji-api:8000/openapi.json`, red Docker **internal**, sin salida externa ni puertos publicados. Frontend: spider/pasivo del build. API: OpenAPI/activo, con límites explícitos de tiempo y 2 hilos. Memoria, Auth/Storage/predictor/generador/embeddings dobles; no se prueba producción ni Supabase compartido.

| Objetivo | Antes válido | Después |
|---|---|---|
| Frontend |2 reglas medias(CSP/marcos),1 baja(nosniff),2 informativas|**0 altas/medias/bajas**,2 informativas|
| API |1 baja(nosniff),2 informativas|**0 altas/medias/bajas**,2 informativas|

Los HTML/JSON originales están en `zap/antes-02/` y `zap/despues/`; comparación en `zap/comparacion.json`. La corrida inicial `zap/antes/` se conserva: su filtro de identidad no aplicó el token ficticio y su API es exploratoria. En las dos corridas válidas se registraron **7465 peticiones API**,7462 con la identidad de prueba;`GET /auth/me` devolvió200 y se recorrieron41 plantillas/rutas distintas, incluido `no_identificada`. No son 7465 funcionalidades ni las 750 transacciones de carga.

Se conservan10027(comentario de dependencia sin secreto confirmado),10109(SPA moderna),100000(respuestas4xx) y 10111(login identificado) como **informativos**. No se cambian reglas a IGNORE. El API posterior termina con 0; el frontend con 2 por sus informativos. El crawler pasivo no demuestra cobertura de toda la UI autenticada, SQL real ni prompt injection. Los códigos/riesgos de los reportes prevalecen frente a la etiqueta WARN de la consola.

ZAP se ejecutó sobre el working tree de 7359a67 con cambios pendientes(`dirty:true` en metadatos); las correcciones se consolidaron en 47107d5. Los JSON registran ese hecho, no se cambia retrospectivamente su commit. Los componentes de negocio protegidos siguen sin diff.

## Repetición de 750 llamadas

La cabecera HTTP se comprobó con el arnés aislado existente, sin cambiar escenarios ni reglas. Commit **e4f4ecf**,750 llamadas únicas,**750 respuestas esperadas,0 fallos inesperados,125 rechazos previstos**, concurrencia4, sin rampa. Duración **45.82s**, throughput **16.37/s**, p50 **233.33ms**, p95 **294.60ms**, p99 **315.59ms**.

PG/pgvector, HTTP, sklearn y DOCX/PDF reales; Auth/Storage/LLM/embeddings y decisión humana simulados. RSS pico239423488 bytes y CPU 434,5% de proceso en convención psutil(100%=un núcleo lógico); no incluye contenedor PG/GPU. No es una comparación causal de mejora ni capacidad productiva de Ollama/Supabase. Se conservan JSONL, muestras y huellas en `carga-750-final/`.

## Understand y pendientes reales

El bloqueo de Understand registrado el26/11 queda superado el27/11 por la ejecución C-06 detallada al inicio. [Resultados y límites](evidencias/understand/README.md); el inventario AST anterior sigue identificado como una herramienta distinta.

La configuración/credenciales/servicio IA estable del destino y su validación operativa quedan pendientes de quien despliegue; fuera del cierre académico. No hay encuestas, actas, métricas ambientales, aceptación institucional ni evaluación humana nuevas. El artículo inglés y las puntuaciones históricas permanecen como antecedentes, sin modificar el manuscrito académico.

## Entrega para despliegue y trazabilidad

Dockerfile con Python/digest fijado, lock runtime, usuario no privilegiado y wheel instalado;`railway.toml`,`deploy/start.py`,`deploy/preflight.py`,`public/_headers`, guía de variables/activación/reversión. No migraciones automáticas ni servicios compartidos modificados. El preflight es offline, no valida credenciales. El build local inicial fallido no se presenta como aprobado; el reintento y la imagen tienen evidencia propia.

Se publica solo la rama independiente para CI;**main y servicios desplegados no se modifican en esta misión**. [Preparación de despliegue](PREPARACION_DESPLIEGUE.md),[observaciones cerradas/pendientes](MATRIZ_OBSERVACIONES_CIERRE.md),[10 HU](matriz_trazabilidad.md),[12 entregables](INDICE_12_ENTREGABLES.md),[ICACIT](ICACIT_EVIDENCIAS.md), informes01–07. Los contenedores PG/ZAP objetivo y su red temporal fueron retirados al finalizar; se conserva la imagen release local. Los logs/reportes originales conservan whitespace de herramientas mediante atributo Git acotado a la carpeta de evidencias; no se relajan reglas de código.

---
## Anexo histórico conservado del cierre anterior

Lo siguiente corresponde al candidato anterior y sus fechas/commits. Las frases históricas sobre aceptación/publicación no describen el alcance actual;prevalece la actualización de arriba. No se suman métricas de corridas distintas.

# Resultados del candidato local NAXJI

Corte: 26/11/2026, América/Lima; los JSON conservan marcas UTC que corresponden al 27/11. Rama `feature/finalizacion-pmv-trazable`, base main `d99f960`. Código final de aplicación probado en `4103c71`; los commits de documentación posteriores no publican ni despliegan el candidato.

## Código entregado

PMV3 incorpora advertencias explicadas, revisión por un revisor en una sola etapa, edición con versiones nuevas, aprobación/rechazo con usuario/fecha/estado, historial, exportación aprobada Word/PDF y auditoría administrativa. El servidor controla propiedad/área/rol y la versión vigente. Estado/evento/versiones se guardan atómicamente; la exportación no invoca IA.

Se conservan PMV1/PMV2, sus puertos, modelos y recursos SQL del commit base. Cambios principales: `revision_informes.py`, `respaldo.py`, repositorios/SQL de revisión, `RevisionInformes.jsx`, exportador PDF, configuración/Auth/Storage y empaquetado. Solo se añade la migración de eventos y semillas piloto optativas; no se aplican a servicios compartidos.

Referencias de revisión: [matriz HU](matriz_trazabilidad.md), [hallazgos](hallazgos_y_correcciones.md), [guía y demo](GUIA_CIERRE_Y_DEMO.md), [ingeniería inversa](ingenieria_inversa.md), [ICACIT](ICACIT_EVIDENCIAS.md), [correcciones académicas](REVISION_ACADEMICA_Y_CORRECCIONES.md) e informes FURPS/OWASP01–07.

## Pruebas reales

| Verificación | Resultado | Evidencia |
|---|---|---|
| Línea base antes de modificar producto | 301 backend aprobadas,21 omitidas;52 frontend; lint/build/diff-check correctos | `evidencias/cierre-trazable/linea-base/` |
| Suite final, PG/pgvector y Ollama reales opt-in | **357 aprobadas,10 omitidas,0 fallidas**;135,80s | `verificacion-final-05/pytest.txt`, `checks.json`, huellas de fuente |
| Frontend actual en Node/JSDOM | **55 aprobadas,0 fallidas** | `verificacion-final-05/frontend.txt` |
| Lint, build y git diff --check | Código0 en los tres | Logs de final-05 |
| QA en venv limpio tras corregir instalación editable | 345 aprobadas,21 omitidas en ese corte; sin IA/Supabase opt-in | `empaquetado/pytest-venv-limpio-corregido.txt` |
| Wheel/sdist del código final | Construidos;46 SQL; API/predictor/plantilla/PDF importados fuera del repo | `empaquetado/wheel-release-resultado.json` y log fuera-repo |
| Word/PDF | Textos de versión guardada comprobados; PDF ficticio renderizado e inspeccionado | Tests PMV3-RAG y `exportaciones-final/` |
| Workflow CI | YAML parseado; acciones/imagen fijadas por hash; permisos de lectura; sin secretos/deploy | `.github/workflows/ci.yml`, `empaquetado/workflow-yaml.txt`; ejecución GitHub pendiente |

La suite final conserva una advertencia de deprecación Starlette/TestClient/httpx en QA. El corte del venv limpio anterior al último caso de permisos tiene un caso menos; no se suman ambas suites como si fueran pruebas distintas. Las corridas fallidas previas se conservan: detectaron fallos reales de pendiente explícito, orden JSONB, referencia E1 e importlib.resources/PEP660.

Las **10 omitidas** finales son:1 de `test_auth_integration.py`,3 de `test_catalogos_supabase.py` y6 de `test_supabase_integration.py`. Requieren cuentas/configuración de un Supabase de pruebas autorizado. No se usaron los secretos ni la base compartida para habilitarlas. En la corrida limpia se omitieron además11 integraciones IA opt-in; en la suite final sí se ejecutaron.

## 750 transacciones del código final

Definición: **una transacción es una llamada HTTP medida**, incluyendo casos negativos planificados; preparación, semillas, arranque y filas de ML no se contabilizan. Concurrencia máxima4, pool fijo por fase dependiente y sin ramp-up. Cada llamada tiene ID único TX-0001…TX-0750.

| Familia | Planificadas / completadas | Rechazos esperados |
|---|---:|---:|
| G1 Accesos/plantillas/catálogos | 150/150 | 10 |
| G2 Solicitudes/validación/propiedad | 200/200 | 75 |
| G3 Predicción/confirmación/contexto | 150/150 | 0 |
| G4 Generación/edición/revisión/historial/auditoría/exportación | 150/150 | 30 |
| G5 Documentos/índice/recuperación/originales | 100/100 | 10 |
| **Total** | **750/750** | **125** |

Resultado: **750 con status esperado,0 fallos inesperados,0 no ejecutadas**. Los125 rechazos por401/403/404/409/422 son casos de control, no errores técnicos ocultos. Tasa de error inesperado0 %. Duración51,24s; throughput14,64 llamadas/s; latencias p50 **261,02ms**, p95 **326,45ms**, p99 **375,40ms**. Las latencias incluyen el cliente HTTP y la respuesta completa, no solo SQL.

Evidencia definitiva: `evidencias/cierre-trazable/carga-750-release/resultado.json`,750 líneas JSONL, muestras de recursos y manifiesto de huellas. Las carpetas anteriores son corridas de candidatos, no se agregan para inflar el total. El throughput por familia del JSON representa su contribución al tiempo total, no un ensayo independiente de cada familia.

Servicios **reales** en la carga: HTTP/FastAPI, sklearn, PostgreSQL/pgvector y DOCX/PDF. **Dobles**: identidad/Auth, Storage en memoria, LLM determinista, embeddings no semánticos y decisión humana simulada. Las pruebas reales de Ollama/bge-m3 son independientes de esta carga. Por ello no se declara capacidad productiva de Ollama/Supabase ni aprobación humana.

Hardware registrado: Windows10.0.26200 según API del sistema,32 CPU lógicas y34.070.192.128 bytes de RAM. Pico RSS del proceso arnés/API255.098.880 bytes; CPU de proceso423,9 % en convención psutil, donde100 % equivale a un núcleo lógico. Se midieron preparación y corrida; se excluyen proceso PostgreSQL del contenedor y GPU. No son mediciones energéticas ni una línea base municipal.

## ML: procedencia y resultados separados

Se localizaron los CSV200/60 y notebooks en Descargas y se leyeron sin copiarlos al repositorio. `auditar_procedencia_ml.py` reconstruyó140/30/30 con semilla42/estratificación normativa y ajustó clones **solo en memoria** para contrastar artefactos. Vocabulario/IDF coinciden; diferencias máximas de coeficientes ≤3e-14; umbral seleccionado0,25 coincide. Los modelos originales no se escribieron ni reemplazaron.

En los30 casos de prueba reconstruidos: accuracy tipo1,0000, macro-F1 sobre las3 clases entrenadas1,0000, F1 micro temático1,0000 y accuracy área1,0000. En el sondeo adicional de60 casos: tipo59/60, área57/60 y F1 micro temático0,9530. No hay solapamiento textual exacto entre CSV60/200, pero eso no acredita independencia de sus patrones, etiquetado o procedencia institucional.

Cero duplicados exactos normalizados en CSV200 no descarta fuga/similitud: el máximo coseno test-train medido fue0,6924. Memorando está en el catálogo y se puede seleccionar manualmente, pero no es una clase entrenada. El macro-F1 de la herramienta sobre4 tipos de catálogo incluye esa clase sin soporte y no debe confundirse con el macro de3 clases del notebook.

Evidencia agregada, hashes/particiones/errores/matrices: `ml/procedencia-particiones-validacion.json`. No se publican sumillas ni notebooks originales. Falta validación institucional independiente y custodia/revisión formal de etiquetas.

## RAG y fuentes

Corpus sintético de3 documentos/8 consultas: embeddings y PG reales;6/6 consultas positivas y2/2 negativas en el escenario declarado. Se conserva como prueba pequeña y no como calidad institucional.

Además se procesó un **PDF MINAM real local**, extracto explícito de páginas físicas23–32:26 fragmentos,6 consultas positivas y2 ajenas. Con el umbral original0,5 y top-k6: **Hit@1=4/6; Hit@k=5/6; rechazo de negativas=2/2**. MINAM-04 no recuperó resultados. No se cambió el umbral después de ver ese fallo. Se comprobó que otro usuario no recibiera el corpus privado.

`rag-minam-real.json` contiene hash del PDF/casos/script, páginas recuperadas, similitudes y tiempos. El etiquetado fue técnico asistido por Codex y por página, no revisión de funcionarios ni prueba de sustento por afirmación. El PDF original no se copió al repositorio. Citar un fragmento no certifica vigencia jurídica, aplicabilidad ni hechos de un expediente.

## Dependencias y seguridad

Auditorías posteriores: npm producción **0 avisos**, árbol completo **0**, pip-audit runtime **33 paquetes/0 avisos**, entorno runtime+QA **41 paquetes/0 avisos conocidos** en esas consultas. Se guardaron JSON antes/después, SBOM CycloneDX Python/npm y locks. Esto no equivale a ausencia de vulnerabilidades desconocidas ni a un escaneo de infraestructura/OS.

Se verifican huellas antes de deserializar joblib; sus bytes se conservan. Para JSON se normalizan únicamente saltos LF/CRLF al contrastar la huella, sin cambiar el archivo original. TLS Storage, no-store, CORS explícito, documentación API opcional y cookies configurables tienen regresiones. Understand no estuvo disponible en PATH/rutas estándar ni se acreditó licencia; no se presenta otra herramienta como Understand.

## Pendientes y entrega

Siguen parciales/bloqueados: Auth/Storage/RLS/revocación reales; cookies del navegador entre sitios; formatos/política de revisión ratificados; servicio IA privado estable; corpus representativo y evaluación humana; Understand/licencia; artículo inglés independiente, aceptación institucional, ahorro y sostenibilidad medidos. No se declara ningún PMV institucionalmente completo.

Se entregan código, commits locales, matrices HU/H/TR,12 salidas de ingeniería inversa,7 atributos ICACIT, informes FURPS/OWASP y guía de demo. **Sin push, PR, merge o despliegue. Main, cambios locales previos y `.env` privados preservados.**

El contenedor PostgreSQL desechable de pruebas fue retirado al finalizar; se conserva el procedimiento para recrearlo. Evidencia: `evidencias/cierre-trazable/limpieza-entorno.json`.

Para versionar los logs se normalizaron saltos de línea y espacios finales sin cambiar resultados; listado en `normalizacion-logs.json`.
