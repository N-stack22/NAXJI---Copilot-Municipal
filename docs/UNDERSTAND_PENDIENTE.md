# SciTools Understand: C-06 completada el 27/11/2026

Se ejecutó **Understand8.1.1269** con la instalación/licencia operativa en Windows sobre la última versión de main **67d9db2f5591c1b08cb85cfe5f81dbd0ad311da9**. Se analizaron149 archivos propios (112Python,37Web);0 errores y224 advertencias de resolución documentadas. Se obtuvieron6.719 líneas de código,141 clases,696 funciones,complejidad máxima26 y mantenibilidad Sonargraph84,44774960712785. Halstead global no está disponible; se publican sus valores reales por archivo/función.

**C-06 cerrada con límites explícitos.** [Todos los resultados CSV/HTML/diagramas](evidencias/understand/README.md), [resumen sin redondear](evidencias/understand/resumen.json), [reproducción corregida y ejecutada](evidencias/understand/REPRODUCIR.md). El bloqueo anterior queda superado; no se cambia el producto ni se publica la licencia.

## Antecedente del 26/11/2026, conservado para trazabilidad

El siguiente diagnóstico corresponde a la instalación anterior. Sus comandos eran orientativos: en8.1.1269 `und -version` no es válido y añadir `src` sin limitar bibliotecas incorpora archivos externos. Para repetir el análisis usar exclusivamente el procedimiento ejecutado enlazado arriba.

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
