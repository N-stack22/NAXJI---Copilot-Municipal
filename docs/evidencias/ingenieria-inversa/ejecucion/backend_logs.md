# Análisis de logs backend

Fuente real: directorios `../../cierre-trazable/linea-base`, `ollama-real*` y `verificacion-final-*`. La línea base aprobó 301 pruebas con 21 omitidas. La verificación final-05 aprobó 357 con 10 omitidas por servicios Supabase reales no autorizados.

Se preservaron fallos detectados: conclusión legacy sin pendiente explícito, orden de claves JSONB y omisión de E1 por el LLM. Sus correcciones y pruebas están en `hallazgos_y_correcciones.md`. Error de datos/estado no publica versiones parciales; errores de proveedor se sanitizan. Persiste una advertencia de deprecación Starlette/TestClient/httpx en QA, sin fallo de la suite. No hay logs de producción ni afirmación de ausencia global de errores.
