# Plan FURPS+

| Hallazgo | Acción compatible | Validación | Reversión / pendiente |
|---|---|---|---|
| F-01 | Advertencias estructurales por sección, motivo y comprobaciones humanas; una sola aprobación por versión | Tests PMV3 de edición/rechazo/aprobación, fuentes inaccesibles y snapshots | Desactivar PMV3 conserva eventos; corpus institucional y juicio humano externos pendientes |
| F-02 | Explicar capa de texto por página y OCR externo antes del reenvío | PDF con texto/mixto/vacío en `test_pmv2.py` | Mantener política de extractor; no simular OCR interno |
| U-01 | Mensaje remoto accionable y conservación de datos/reintentos | Frontend, HTTP simulado y lint/build | Volver al formateador anterior si hay regresión; conservar errores HTTP específicos |
| R-01 | `/ready` privado, de lectura y con tiempos acotados; mantener `/health` | Tests de caída, sanitización y permisos | Retirar el monitor nuevo sin alterar liveness |
| P-01 | Medir HTTP por familias, latencias, throughput y recursos; evaluar RAG real separadamente | 750 llamadas aisladas; PGvector real y bge-m3 | No cambiar ranking/filtros ni afirmar capacidad productiva con dobles |
| S-01 | Entrada canónica pyproject, compatibilidad requirements y wheel/SQL/modelos/plantilla | Instalación en venv nuevo, importación fuera del repo, pruebas de recursos | Revertir manifiesto/lock como unidad; no tocar entornos privados |
| X-01 | Guía de activación con migraciones explícitas, bucket privado y perfiles | Suite en bases aleatorias; lista operativa | RAG/PMV3 siguen opt-in; sin despliegue compartido autorizado |

Responsables propuestos por función: desarrollo para código; QA para pruebas; titular de infraestructura para servicios/permisos; revisor institucional para fuentes/formatos. No se asignaron personas ni fechas de aceptación inexistentes. Los bloqueos externos permanecen abiertos hasta obtener evidencia.
