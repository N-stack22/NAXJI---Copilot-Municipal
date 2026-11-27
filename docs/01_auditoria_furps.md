# Auditoría FURPS+: diagnóstico contrastado

Fuente: guías FURPS/OWASP proporcionadas, hallazgos F-01…X-01. El 14/24 del documento del 13/11 es una calificación histórica; no una ejecución actual. Se contrastó main d99f960 y se ejecutó la línea base: 301 pruebas backend, 21 omitidas y 52 frontend, con PG aislado. Logs en `evidencias/cierre-trazable/linea-base/`.

| ID / dimensión | Evidencia de la brecha | Impacto / prioridad |
|---|---|---|
| F-01 / Funcionalidad | `vincular_citas` valida identificadores/pasajes, no implicación semántica ni vigencia | Alto: revisión humana necesaria; PMV3 no estaba implementado |
| F-02 / Funcionalidad | `extractor.py` rechaza todo PDF con una página sin texto | Medio: el reintento del mismo PDF no ayuda; orientar a OCR externo |
| U-01 / Usabilidad | `api.js` sugería siempre encender 127.0.0.1 incluso desde una web publicada | Medio: orientación errónea ante un servicio remoto caído |
| R-01 / Fiabilidad | `/health` era únicamente liveness, sin disponibilidad operativa diferenciada | Alto: podía informar proceso vivo con dependencias caídas |
| P-01 / Rendimiento | SQL exacto materializa corpus autorizado antes de ordenar; no había carga actual de 750 | Alto: costo dependiente de volumen; no sacrificar permisos para optimizar |
| S-01 / Mantenibilidad | Divergencia de requirements frente a pyproject y archivo PMV2 | Alto para instalación limpia; dependencias documentales podían faltar |
| X-01 / Restricciones | RAG desactivado por defecto; configuración externa no verificada | Alto para aceptación: código presente no equivale a flujo activo |

Método: inspección de rutas/puertos/adaptadores y pruebas locales; no se inspeccionó ni modificó producción. Nuevos defectos de integración encontrados durante esta tarea se registran en `hallazgos_y_correcciones.md`.
