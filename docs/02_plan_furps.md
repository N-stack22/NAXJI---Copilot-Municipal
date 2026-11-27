# Plan FURPS+ ejecutado

Base `main` **7359a67**. Los **3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Las pruebas omitidas conservan ese estado. No se modifican pilotos, predictor, RAG, HU-IA-04, esquema ni documentos académicos originales.

| Acción | Implementación mínima | Validación | Estado |
|---|---|---|---|
| Reforzar arquitectura | Resolver imports absolutos/relativos, alias, dominio hacia aplicación y recorridos completos | Casos adversarios y carga de todos los módulos | Cerrada; sin infracciones productivas |
| Reforzar SQL | Descubrimiento recursivo, comentarios, literales partidos/f-strings y recursos por alias | Adaptador nuevo anidado; 46 recursos legibles fuera del repo | Cerrada; adaptadores intactos |
| Contrastar seguridad HTTP | ZAP antes/después en red sin salida externa | HTML/JSON y cobertura autenticada de laboratorio | Cerrada en alcance |
| Corregir cabeceras confirmadas | nosniff en API; CSP/marcos/nosniff en archivo estático | 6 regresiones y reescaneo | Cerrada localmente |
| Comprobar entrega | pytest/frontend/lint/build/wheel/sdist/Docker/CI | Logs con commit y resultado; prueba de imagen sin red | Ejecutada; ver resultados por corrida |
| Repetir rendimiento HTTP | Mantener el arnés y sus dobles declarados | 750/750 con status esperado, 0 fallos inesperados | Cerrada en laboratorio |
| Medir con Understand | Comprobar instalación y licencia; ejecutar solo si disponibles | PATH, rutas y registro; guía oficial manual | Bloqueada, no simulada |

Rollback de estas correcciones: volver al commit anterior de la rama o a una imagen previa compatible. No se borran informes/versiones/eventos ni se aplican migraciones. Los modos y banderas de PMV mantienen su política existente.

Evidencia actual: [resultados](RESULTADOS_CIERRE.md), [observaciones cerradas y pendientes](MATRIZ_OBSERVACIONES_CIERRE.md), [12 entregables](INDICE_12_ENTREGABLES.md) y [preparación de despliegue](PREPARACION_DESPLIEGUE.md). Los logs históricos de `evidencias/cierre-trazable/` se conservan; no se suman suites repetidas para inflar resultados.
