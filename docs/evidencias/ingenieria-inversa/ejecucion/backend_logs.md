# Prompt 6 — Análisis vigente de logs backend

Corte documental 27/11/2026, main **4f4d294**. Se revisan logs existentes; no se repiten pruebas ni se leen logs de producción. Cada resultado conserva commit, entorno y alcance.

| Registro | Resultado/límite verificable |
| ---| ---|
| [CI 4 f 4 d 294](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611), [extracto previo de la misma entrega C-06](../../understand/ci-main-extracto.log) | 375 backend a probadas, 21 optativas omitidas, 1 advertencia; no sumar corridas repetidas. |
| [CI histórico seguridad](../../cierre-seguridad-20261126/ci/ejecuciones.json) | Fallo por checkout superficial y repeticiones posteriores conservados; no se oculta el fallo. |
| [Carga 750](../../cierre-seguridad-20261126/carga-750-final/resultado.json), [transacciones](../../cierre-seguridad-20261126/carga-750-final/transacciones.jsonl) | 750/750 resultados esperados, 0 errores inesperados, 125 rechazos previstos. HTTP yPG reales; Auth/Storage/LLM/embeddings y decisiones humanas con dobles declarados. |
| [ZAP posterior](../../cierre-seguridad-20261126/zap/despues/api-funcionario.json) | Sin alertas altas/medias/bajas posteriores en el objetivo local analizado; informativos conservados. No una prueba productiva ni de toda laUI. |
| [Understand analisis.log](../../understand/analisis.log), [advertencias.json](../../understand/advertencias.json) | 0 errores/224 advertencias:156 importsPython estándar, 61 tercerosPython, 6 tercerosWeb y 1 rutaVite no resuelta desde HTML. No se ocultan ni se confunden con excepciones de aplicación. |

La advertencia deprecada Starlette/TestClient/httpx sigue registrada; no es una prueba fallida. Las 21 omitidas requieren 10 integracionesSupabase/Auth y 11 Ollama/embeddings, no se contabilizan como a probadas. El [manejo de errores](../../../../src/main.py) devuelve mensajes sanitizados yel [dominio](../analisis/dominio.md) describe los conflictos de estado.

Las cifras 301/357 del antecedente pertenecen a cortes anteriores. [Resultados consolidados](../../../RESULTADOS_CIERRE.md), [fallos históricos y correcciones](../../../hallazgos_y_correcciones.md). Este análisis no de muestra ausencia global de errores, capacidad externa ni validez institucional.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Análisis de logs backend

Fuente real: directorios `../../cierre-trazable/linea-base`, `ollama-real*` y `verificacion-final-*`. La línea base aprobó 301 pruebas con 21 omitidas. La verificación final-05 aprobó 357 con 10 omitidas por servicios Supabase reales no autorizados.

Se preservaron fallos detectados: conclusión legacy sin pendiente explícito, orden de claves JSONB y omisión de E1 por el LLM. Sus correcciones y pruebas están en `hallazgos_y_correcciones.md`. Error de datos/estado no publica versiones parciales; errores de proveedor se sanitizan. Persiste una advertencia de deprecación Starlette/TestClient/httpx en QA, sin fallo de la suite. No hay logs de producción ni afirmación de ausencia global de errores.
