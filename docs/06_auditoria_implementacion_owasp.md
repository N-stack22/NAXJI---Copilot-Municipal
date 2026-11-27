# Verificación de las correcciones OWASP2021

Base `main` **7359a67**. Los **3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Las pruebas omitidas conservan ese estado. No se modifican pilotos, predictor, RAG, HU-IA-04, esquema ni documentos académicos originales.

| Objetivo | Antes válido (`antes-02`) | Después (`despues`) | Estado |
|---|---|---|---|
| Frontend build | 2 reglas medias,1 baja,2 informativas | 0 altas/medias/bajas;2 informativas | Cabeceras corregidas en configuración estática emulada |
| API de laboratorio | 1 regla baja,2 informativas | 0 altas/medias/bajas;2 informativas | nosniff corregido en API |
| Acceso autenticado del scanner | /auth/me200; identidad ficticia presente en7462 de7465 peticiones | Misma evidencia de cobertura | La identidad de prueba sí se aplicó |

Las7465 peticiones por corrida de API y las750 de carga son ensayos distintos; no se mezclan. ZAP recorrió41 plantillas de ruta incluyendo respuestas negativas y rutas no identificadas. Las variantes de ataques no equivalen a nuevas funcionalidades probadas.

Persisten informativos10027/10109 en frontend y100000/10111 en API. No se encontró un secreto en la muestra del comentario. Los4xx no se cuentan como fallos500. No se demuestra con esto ausencia universal de vulnerabilidades, cobertura de toda la UI autenticada ni seguridad de servicios reales.

Regresiones: `tests/test_cabeceras_seguridad.py` (6 casos); suite completa375/21 y55 frontend. Se conservan SQL, transacciones, permisos, predictor, RAG y advertencias. JSON comparativo: `evidencias/cierre-seguridad-20261126/zap/comparacion.json`.

Evidencia actual: [resultados](RESULTADOS_CIERRE.md), [observaciones cerradas y pendientes](MATRIZ_OBSERVACIONES_CIERRE.md), [12 entregables](INDICE_12_ENTREGABLES.md) y [preparación de despliegue](PREPARACION_DESPLIEGUE.md). Los logs históricos de `evidencias/cierre-trazable/` se conservan; no se suman suites repetidas para inflar resultados.
