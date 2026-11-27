# Remediación OWASP2021 ejecutada

Base `main` **7359a67**. Los **3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Las pruebas omitidas conservan ese estado. No se modifican pilotos, predictor, RAG, HU-IA-04, esquema ni documentos académicos originales.

| ID | Hallazgo confirmado / tratamiento | Archivo | Comprobación |
|---|---|---|---|
| Z-01 | Content-Security-Policy ausente: política de scripts/estilos propios, sin inline/eval, objetos/base/marcos prohibidos | `public/_headers` | Regla10038 media antes; ausente después |
| Z-02 | Protección contra marcos ausente: frame-ancestors none y X-Frame-Options DENY | `public/_headers` | Regla10020 media antes; ausente después |
| Z-03 | nosniff ausente en frontend/API; incluir respuestas y errores500 | `public/_headers`, `src/main.py` | Regla10021 baja antes; ausente después; regresiones200/401/404/422/500 |
| Z-04 | Comentario del bundle señalado informativamente | Sin editar dependencia ni funciones | Muestra: texto genérico de implementación, sin secreto confirmado |
| Z-05 | SPA moderna / login / respuestas4xx informativos | Sin suprimir reglas | Se registran como límites de cobertura y respuestas de validación/control |
| CI-01 | Referencia7359a67 ausente en checkout superficial | `.github/workflows/ci.yml` fetch-depth0 | Fallo real conservado; ejecución repetida exitosa |
| DEP-01 | Timeout real descargando PyPI en build local | `Dockerfile`: caché por capa, timeout/reintentos | Log fallido y reintento exitoso conservados; lock no cambia |

No se usan IGNORE ni filtros para esconder alertas. Los códigos de ZAP se interpretan según su herramienta:2 puede significar avisos incluso informativos;0 del API posterior no equivale a certificación. La política del frontend se prueba con una emulación local del archivo de Cloudflare, no contra el servicio publicado.

Evidencia actual: [resultados](RESULTADOS_CIERRE.md), [observaciones cerradas y pendientes](MATRIZ_OBSERVACIONES_CIERRE.md), [12 entregables](INDICE_12_ENTREGABLES.md) y [preparación de despliegue](PREPARACION_DESPLIEGUE.md). Los logs históricos de `evidencias/cierre-trazable/` se conservan; no se suman suites repetidas para inflar resultados.
