# SciTools Understand: bloqueo real y procedimiento reproducible

No se encontró `und`/`understand` en PATH, seis rutas estándar ni aplicaciones registradas de Windows. Evidencia: [disponibilidad.json](evidencias/cierre-seguridad-20261126/understand/disponibilidad.json). No se pudo verificar una licencia ni ejecutar análisis. **Complejidad, dependencias y mantenibilidad de Understand: no medidas.** El CSV de imports AST es otra herramienta y no se atribuye a Understand.

En una máquina con instalación y licencia válidas, desde la raíz de esta rama, ejecutar los siguientes comandos en PowerShell. Guardar versión, errores y salida en un directorio nuevo; no ejecutar contra una base Understand anterior que deba conservarse.

```powershell
und -version
und help create
und -db NAXJI-cierre.und create -languages Python Web
und -db NAXJI-cierre.und add src
und -db NAXJI-cierre.und analyze
und metrics -metrics CountLineCode Cyclomatic CyclomaticStrict HalsteadMaintainIdx understand-metricas.csv NAXJI-cierre.und
und export -dependencies file csv understand-dependencias.csv NAXJI-cierre.und
```

Si la sintaxis o una métrica no está soportada por la versión instalada, consultar `und help metrics` y `und help export`. No reemplazar valores no disponibles por cero. Revisar errores de parseo, en especial JSX, registrar lenguaje/dialecto reconocido y excluir `node_modules`, `.venv`, `dist` y evidencias. En GUI: Project → Configure Project → Languages; Metrics → Export Metrics; Project → Export Dependencies → File Dependencies → Export CSV. Para el HTML usar el reporte de complejidad disponible en Reports, conservando la versión y la configuración.

Interpretar `HalsteadMaintainIdx` conforme a su definición y al soporte por entidad, sin convertirlo en porcentaje de calidad ni acreditar mantenibilidad si está vacío. Adjuntar el commit analizado y el listado de archivos de la base.

Fuentes oficiales: [CLI](https://docs.scitools.com/help/automate/und-cli.html), [exportar métricas](https://docs.scitools.com/help/metrics/export-and-track-metrics.html), [dependencias](https://docs.scitools.com/help/dependencies/browse-and-export-dependencies.html), [mantenibilidad](https://docs.scitools.com/metrics/HalsteadMaintainIdx.html), [lenguajes](https://docs.scitools.com/help/getting-started/supported-languages.html).
