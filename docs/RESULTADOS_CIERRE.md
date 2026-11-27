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
