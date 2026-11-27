# Consolidación de los 12 entregables de ingeniería inversa

Se organiza la evidencia ya producida para las consignas suministradas, sin agregar requisitos de producto. Base funcional7359a67;corte de seguridad en esta rama. El informe integral y los archivos históricos se mantienen, y la actualización de pruebas está en `evidencias/cierre-seguridad-20261126/`. Las salidas AST no son resultados de Understand.

| N.º | Entregable consolidado | Archivo(s) | Contraste actual |
|---|---|---|---|
|1|Inventario y recorrido inicial de ingeniería inversa|`evidencias/ingenieria-inversa/auditoria/inventario_archivos.md` y `analisis/modulos.md`|AST110 módulos;inventario completo de imports;esquema y componentes protegidos sin diff|
|2|Descubrimiento funcional|`evidencias/ingenieria-inversa/analisis/casos_uso.md`|10 HU aceptadas;375 pruebas backend y55 frontend|
|3|Descubrimiento tecnológico|`evidencias/ingenieria-inversa/auditoria/stack_tecnologico.md`|FastAPI/ReactJSX/sklearn/Ollama/PGvector conservados;runtime Linux de Docker/CI|
|4|Detección arquitectónica|`evidencias/ingenieria-inversa/auditoria/arquitectura_detectada.md`|Guardias relativas/absolutas y dominio→aplicación;0 infracciones|
|5|Reconstrucción del entorno|`evidencias/ingenieria-inversa/configuracion/{instalacion,servicios,variables_entorno}.md`|Dockerfile,Railway,Cloudflare y preflight sin secretos;no servicios compartidos|
|6|Dependencias|`evidencias/ingenieria-inversa/dependencias/{backend,frontend,infraestructura}.md`|Locks/SBOM históricos;599 referencias AST actuales;16 adaptadores/46SQL|
|7|Análisis de logs|`evidencias/ingenieria-inversa/ejecucion/{backend_logs,frontend_logs,endpoints_detectados}.md`|Línea base,nueva suite,carga,ZAP y CI con fallos conservados|
|8|Reconstrucción arquitectónica|`evidencias/ingenieria-inversa/analisis/arquitectura_real.md`|Sin cambios de negocio;solo cabeceras HTTP y entrega/QA|
|9|Reconstrucción del dominio|`evidencias/ingenieria-inversa/analisis/dominio.md`|Entidades/estados/reglas y HU-IA-04 sin diff respecto de7359a67|
|10|Evaluación arquitectónica|`evidencias/ingenieria-inversa/analisis/calidad_arquitectura.md`|Guardias reforzadas;Understand bloqueado, sin métricas inventadas|
|11|Hallazgos|`evidencias/ingenieria-inversa/analisis/hallazgos.md` y `hallazgos_y_correcciones.md`|C-01…C-12 con cerrados,informativos,bloqueados y fuera de alcance|
|12|Generador final / informe integrado|`ingenieria_inversa.md`|Consolida arquitectura,FURPS+,OWASP2021,ICACIT y referencias a resultados actuales|

Rutas entre llaves agrupan archivos existentes, no archivos nuevos con ese nombre literal. [Resultados](RESULTADOS_CIERRE.md), [matriz de observaciones](MATRIZ_OBSERVACIONES_CIERRE.md), [despliegue](PREPARACION_DESPLIEGUE.md).
