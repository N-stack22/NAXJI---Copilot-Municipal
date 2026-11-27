# Verificación de mejoras FURPS+

| ID | Resultado técnico | Riesgo residual / estado |
|---|---|---|
| F-01 | Motivos por sección; edición/rechazo; decisión y justificaciones ligadas a versión; fuente inaccesible impide aprobación | **Parcial**: no certifica pertinencia semántica/jurídica ni reemplaza al revisor |
| F-02 | Mensaje explica OCR y evita recomendar repetir el mismo archivo; no se omiten páginas a escondidas | **Verificado local**; OCR externo sigue requerido |
| U-01 | El sitio publicado ya no indica una dirección local como solución | **Verificado local** con frontend; disponibilidad real sigue dependiendo del despliegue |
| R-01 | Liveness estable; readiness requiere administrador y devuelve 503 con una dependencia caída | **Verificado local**; permisos efectivos institucionales no certificados |
| P-01 | Registros reales de 750 llamadas y recursos; embeddings/PG reales en pruebas separadas | **Parcial**: carga con Auth/Storage/LLM/embeddings dobles; no costo energético ni escalabilidad productiva |
| S-01 | Dependencias unificadas, wheel instalado fuera del árbol, 46 SQL incluidos | **Verificado Windows/Python 3.11**; instalación Linux por verificar |
| X-01 | Migración nueva aditiva/idempotente; configuración y demo documentadas | **Parcial**: activación en servicios reales pendiente |

Evidencias: `test_pmv3*.py`, `test_seguridad_cierre.py`, `test_cierre_pmv1.py`, `test_sql_resources.py`, `test_arquitectura.py`, pruebas frontend y `evidencias/cierre-trazable/`. Los directorios de verificación incluyen sus códigos de salida; no se ocultan las corridas que detectaron defectos.

Valoración académica provisional, usando la escala 0–4 de la guía (0 sin control, 1 inicial, 2 parcial, 3 brecha acotada, 4 completo en el criterio): Funcionalidad 2, Usabilidad 3, Fiabilidad 3, Rendimiento 2, Mantenibilidad 3, Restricciones 2: **15/24**. Es juicio de cobertura del alcance inspeccionado, no una medición de calidad universal ni aceptación institucional. Persiste una advertencia de deprecación Starlette/TestClient/httpx en QA.
