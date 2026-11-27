# Auditoría FURPS+: línea base y alcance académico

Actualización27/11/2026: **C-06 ejecutada con Understand8.1.1269** sobre main67d9db2. La dimensión soporte/mantenibilidad cuenta ahora con métricas reales del backend y frontend:149 archivos,141 clases,696 funciones,6.719 líneas de código;complejidad máxima26 y SonargraphMaintainability84,44774960712785. Halstead por archivo, fan-in/fan-out y acoplamiento de clases se entregan sin rellenar valores no disponibles. [CSV/HTML/diagramas y límites](evidencias/understand/README.md). No se cambian producto ni evaluación de funcionalidad/usabilidad/rendimiento; las mediciones anteriores conservan su corte.

Base `main` **7359a67**. Los **3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Las pruebas omitidas conservan ese estado. No se modifican pilotos, predictor, RAG, HU-IA-04, esquema ni documentos académicos originales.

Línea base de esta misión: **346 pruebas backend aprobadas, 21 omitidas**, 55 frontend, lint/build/diff correctos; `7359a67`. No se atribuyen a esta corrida las 11 integraciones IA reales del cierre anterior.

| Dimensión | Observación comprobada | Evidencia y alcance |
|---|---|---|
| Funcionalidad | Las diez HU ya están implementadas y aceptadas; no corresponde reimplementarlas | Matriz HU, suites PMV1/2/3 y capturas existentes |
| Usabilidad | Interfaz y mensajes vigentes se conservan | 55 pruebas Node/JSDOM; no equivalen a SUS ni encuesta |
| Fiabilidad | Permisos, versiones, bloqueos y atomicidad existentes se mantienen | PostgreSQL/pgvector desechable; no base compartida |
| Rendimiento | Un cambio de cabecera HTTP requiere comprobar regresión de entrega | Repetición de 750 llamadas; no ensayo de servicios IA reales |
| Mantenibilidad | Guardias antiguas no resolvían relativos y SQL tenía lista fija | Nuevas guardias recorren 110 módulos y 16 módulos de persistencia |
| Restricciones (+) | Faltaban archivos explícitos para despliegue por imagen/headers | Dockerfile, PORT, salud, Railway y Cloudflare; sin desplegar |

No se renuevan porcentajes de calidad a partir de resultados parciales. Las puntuaciones de guías anteriores son antecedentes, no métricas medidas en esta misión.

Evidencia actual: [resultados](RESULTADOS_CIERRE.md), [observaciones cerradas y pendientes](MATRIZ_OBSERVACIONES_CIERRE.md), [12 entregables](INDICE_12_ENTREGABLES.md) y [preparación de despliegue](PREPARACION_DESPLIEGUE.md). Los logs históricos de `evidencias/cierre-trazable/` se conservan; no se suman suites repetidas para inflar resultados.
