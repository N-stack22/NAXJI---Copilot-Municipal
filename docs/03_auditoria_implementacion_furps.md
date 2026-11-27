# Verificación FURPS+ del cierre

Base `main` **7359a67**. Los **3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Las pruebas omitidas conservan ese estado. No se modifican pilotos, predictor, RAG, HU-IA-04, esquema ni documentos académicos originales.

| Dimensión | Resultado real | Límite |
|---|---|---|
| F | 375 backend aprobadas, 21 omitidas; 10 HU aceptadas | Las omitidas no están aprobadas |
| U | 55 frontend aprobadas; JSX y pantallas sin cambios | JSDOM no es evaluación por usuarios |
| R | Persistencia/transacciones y permisos siguen verdes; imagen en solo lectura, usuario10001, PORT 8088 y salud200 | Salud es liveness; servicios externos no conectados |
| P | 750 llamadas: 0 fallos inesperados; 125 rechazos previstos; p95=294,60ms; throughput16,37/s | Dobles Auth/Storage/LLM/embeddings; sin comparación causal con otro equipo ni SLO productivo |
| S | 110 módulos/599 referencias revisados; 16 módulos persistencia; 46 SQL; wheel/sdist y Linux Docker/CI | Complejidad y mantenibilidad de Understand no medidas |
| + | Docker/railway.toml/preflight/_headers y procedimiento de reversión | Configuración de destino y promoción no ejecutadas |

No se asigna una nueva nota FURPS a partir de estas pruebas. La advertencia Starlette/TestClient/httpx sigue registrada en QA. Se preservan pilotos y artefactos de modelos; no se altera la recuperación para mejorar una métrica.

Evidencia actual: [resultados](RESULTADOS_CIERRE.md), [observaciones cerradas y pendientes](MATRIZ_OBSERVACIONES_CIERRE.md), [12 entregables](INDICE_12_ENTREGABLES.md) y [preparación de despliegue](PREPARACION_DESPLIEGUE.md). Los logs históricos de `evidencias/cierre-trazable/` se conservan; no se suman suites repetidas para inflar resultados.
