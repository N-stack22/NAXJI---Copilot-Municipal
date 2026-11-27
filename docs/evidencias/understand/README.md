# C-06 — SciTools Understand ejecutado

Corte: **27/11/2026, América/Lima**. Analizado `main` en **67d9db2f5591c1b08cb85cfe5f81dbd0ad311da9**, última versión remota comprobada antes y después del análisis. Herramienta real **SciTools Understand 8.1.1269**, Windows, licencia operativa acreditada por la ejecución. No se distribuyen la licencia ni la base `.und`.

**C-06 cerrada como ejecución y entrega de evidencia**, con las limitaciones explícitas siguientes. No se declara certificación de calidad, aceptación institucional ni ausencia de defectos a partir de métricas estáticas. El código del producto, esquema, PMV, plantillas, ML y RAG no cambian.

## Resultados medidos

| Medida | Resultado | Interpretación |
|---|---:|---|
| Archivos propios | 149 | 112 Python y 37 Web; [lista exacta](alcance-archivos.json), [huellas de fuentes](fuentes-sha256.json) |
| Líneas físicas / de código / comentarios | 8.807 / 6.719 / 248 | Métricas Understand, no un conteo de todo el repositorio |
| Clases / funciones | 141 / 696 | Definiciones exportadas; las funciones incluyen métodos y funciones anidadas según el lenguaje |
| Métodos, métrica nativa del proyecto | 224 | Subconjunto; **no sumar a las 696 funciones**. La métrica no está disponible por archivo |
| Complejidad ciclomática máxima / mediana | 26 / 1 | Mediana calculada sobre las 696 definiciones; `AvgCyclomatic` nativo del proyecto = 2; `SumCyclomatic` = 1.549 |
| Mantenibilidad Sonargraph nativa del proyecto | 84,44774960712785 | Implementación ML2 de Understand, basada en dependencias; no equivale a 84,45% de calidad ni a una medición con Sonargraph independiente |
| Halstead original por archivo, valores distintos de cero | 141 | Mínimo −55,4200; mediana 81,0988; máximo 263,2070. Sin normalizar, no porcentaje ni límite 0–100 |
| Halstead del proyecto | No disponible | `null`, no se sustituye por cero. Se conservan también los 8 ceros nativos de archivos y sus advertencias de interpretación |
| Fan-in / fan-out por archivo | Medianas 2 / 3; máximos 34 / 42 | Dependen de las referencias resueltas; métricas del proyecto no disponibles |
| Relaciones dirigidas entre archivos propios | 423 | [CSV con rutas completas del repositorio](dependencias-rutas.csv) y [agregación por capas](dependencias-capas.csv) |
| Dependencias prohibidas resueltas desde dominio/aplicación | 0 | [Reglas y alcance](verificacion-hexagonal.json); no demuestra ausencia de imports dinámicos |

Los valores sin redondear, las métricas no disponibles y las agregaciones se distinguen en [resumen.json](resumen.json). El acoplamiento entre clases se conserva en los reportes por clase, sin inventar un escalar global.

## Archivos y reportes

Para consultar las métricas y navegar el conjunto sin depender de GitHub, descargar [reportes-understand.zip](reportes-understand.zip), extraerlo y abrir `index.html`; también está disponible [la carpeta completa](.). Esta vista está identificada como derivada de los valores API; no sustituye los reportes nativos. Las [huellas de los artefactos publicadas en GitHub](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/evidencias/understand/SHA256SUMS.json) permiten comprobar los archivos descargados. El ZIP contiene las evidencias de esta carpeta salvo el propio ZIP y su manifiesto exterior de huellas.

| Resultado | Enlaces |
|---|---|
| CSV nativo completo | [metricas-nativas.csv](metricas-nativas.csv) |
| Métricas con rutas y valores API sin redondear | [Archivos](metricas-archivos.csv), [funciones](metricas-funciones.csv), [clases](metricas-clases.csv) |
| Mantenibilidad y acoplamiento | [Halstead por archivo](mantenibilidad-archivos.csv), [fan-in/fan-out](acoplamiento-archivos.csv) |
| Dependencias | [CSV nativo](dependencias-nativas.csv), [CSV API con rutas](dependencias-rutas.csv), [capas](dependencias-capas.csv) |
| HTML nativos de complejidad, líneas y clases | [Complejidad](reportes/complejidad/path_0.html), [líneas](reportes/lineas/path_0.html), [clases](reportes/clases/index.html) |
| HTML nativos de mantenibilidad | [Funciones](reportes/mantenibilidad-funciones/index.html), [clases](reportes/mantenibilidad-clases/index.html) |
| HTML nativos de acoplamiento | [Control](reportes/acoplamiento-control/index.html), [datos](reportes/acoplamiento-datos/index.html) |
| Diagramas nativos | [Dependencias hexagonales SVG](diagramas/hexagonal-dependencias.svg), [PNG](diagramas/hexagonal-dependencias.png), [estructura](diagramas/hexagonal-estructura.svg), [dependencias entre archivos](diagramas/dependencias-archivos.svg), [funciones complejas](diagramas/funciones-complejas.svg) |
| Arquitectura exportada | [XML nativo](arquitectura-nativa.xml) |
| Configuración, ejecución y limitaciones | [Configuración](configuracion.json), [log de análisis](analisis.log), [advertencias](advertencias.json), [reproducción](REPRODUCIR.md) |
| Validación complementaria | [27 pruebas de arquitectura/SQL](pruebas-arquitectura-sql.log), [verificación de artefactos](verificacion-artefactos.json) |
| GitHub Actions de la entrega | [Resultados375/21 backend,55 frontend y comprobaciones](CI.md), [pasos recibidos de GitHub](ci-main.json), [extracto literal](ci-main-extracto.log) |

Los HTML se descargan y abren localmente, conservando sus archivos hermanos `path_*.html`, `image*.png` y `table*.csv`. GitHub muestra el código HTML. Los PNG/CSV disponibles en cada carpeta son exportaciones nativas; los reportes sin gráfico no producen PNG. Los reportes «Low Maintainability» aplican las reglas propias del reporte, no constituyen un índice Halstead global. El XML conserva las referencias relativas de la base privada original; para otra ubicación conviene reconstruir los grupos con el exportador.

## Análisis y decisiones

1. **Complejidad localizada:** `ExportadorDocx.exportar` alcanza 26; `GeneradorBorradorOllama.generar`, 22; `validar_fidelidad_inspeccion`, 20; `FormularioInforme`, 18. Son candidatos a revisión futura, no fallos funcionales demostrados. No se refactorizan ni se modifican RAG, modelos o PMV para reducir una cifra.
2. **Mantenibilidad localizada:** `NuevoInforme.jsx` tiene Halstead original −55,4200. La fórmula combina volumen, complejidad estricta, líneas y comentarios; el resultado negativo es nativo, no un error corregido manualmente. Los valores superiores a 100 también se conservan. Las funciones Web con cero nativo se entregan tal como las devuelve esta versión, sin interpretarlas como mantenibilidad nula.
3. **Arquitectura hexagonal:** dominio depende solo de dominio; aplicación, solo de aplicación/dominio en las relaciones propias resueltas. El frontend tiene relaciones internas. El ciclo exterior infraestructura/adaptadores de salida es visible en el diagrama y corresponde a composición/configuración y acceso a configuración; no implica una inversión del núcleo ni prueba un defecto. Las 27 guardias AST/SQL complementan esta evidencia con imports relativos y dinámicos literales.
4. **Acoplamiento:** las clases de composición y orquestación aparecen entre las más acopladas en los CSV. No se aplica un umbral de aprobación inventado; hay que considerar su función arquitectónica y los imports excluidos.
5. **Sin defecto técnico de producto confirmado:** solo se corrigen la evidencia pendiente y las instrucciones de reproducción. No se ejecutan migraciones, no se contacta producción y no se toca `.env` ni Supabase compartido.

## Límites del análisis

El análisis final termina con **0 errores y 224 advertencias**. De ellas, 223 corresponden a imports de bibliotecas estándar/de terceros excluidas; una corresponde a `/src/adapters/in/web/main.jsx` en `index.html`, una ruta absoluta válida para Vite que Understand no resuelve desde HTML. Ese JSX sí figura analizado individualmente en el manifiesto. No se cambia una ruta funcional para silenciar el analizador.

La base contiene 5 archivos simbólicos estándar suministrados por Understand (`abc`, `builtins`, `datetime`, `math`, `unicodedata`). No se cuentan como código propio. Los totales nativos coinciden con la suma de los 149 archivos propios para líneas, clases y funciones. Los reportes de complejidad/líneas/clases se limitan a la arquitectura de archivos propios. Los otros cuatro reportes admiten proyecto y pueden mostrar relaciones con símbolos externos; esos símbolos no se presentan como código analizado de dependencias.

Se excluyen bibliotecas instaladas, `node_modules`, `.venv`, builds, pruebas, documentación, binarios ML y plantillas. Esto limita la resolución interbibliotecas, y no valida llamadas HTTP entre frontend/backend, comportamiento dinámico, seguridad o rendimiento. La carga 750 y los reportes ZAP previos permanecen históricos; no se repiten porque no cambia el producto ni su rendimiento.

La exportación CLI de dependencias de una arquitectura personalizada devolvió «missing some arguments» en esta versión incluso con la sintaxis documentada. No se simula ese CSV: se entregan el CSV nativo de dependencias **de archivos**, los diagramas nativos de la arquitectura y la agregación CSV identificada como derivada de `Ent.depends()`.

El HTML nativo de complejidad exporta la portada y las siete capas, pero conserva enlaces a páginas de detalle por archivo que no genera. Se preserva el original y se registra el límite en la verificación de artefactos. El detalle completo está disponible en los CSV y en la vista derivada `index.html`; no se afirma que esos enlaces nativos funcionen.

Fuentes de interpretación: [catálogo oficial Halstead](https://docs.scitools.com/metrics/HalsteadMaintainIdx.html), [fan-out oficial](https://docs.scitools.com/metrics/DirectFanOut.html), ayuda local `und help report/export/metrics` e implementación instalada `plugins/Metric/sonargraph_maintainability.upy` (ML2, sin copiar el plugin).

## Informes técnicos actualizados en main

[FURPS+ auditoría](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/01_auditoria_furps.md), [plan](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/02_plan_furps.md), [verificación](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/03_auditoria_implementacion_furps.md), [dictamen final](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/07_auditoria_final.md), [ICACIT](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/ICACIT_EVIDENCIAS.md), [ingeniería inversa](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/ingenieria_inversa.md), [12 entregables](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/INDICE_12_ENTREGABLES.md), [resultados de cierre](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/RESULTADOS_CIERRE.md) y [matriz de observaciones](https://github.com/N-stack22/NAXJI---Copilot-Municipal/blob/main/docs/MATRIZ_OBSERVACIONES_CIERRE.md). El informe académico final permanece intacto.
