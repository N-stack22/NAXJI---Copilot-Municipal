> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Inventario de archivos

Escaneo local de `src`: dominio 18 archivos Python; aplicación 31; adaptadores 52; infraestructura 8 al corte de esta reconstrucción. El detalle de clases, rutas y conteos está en `../../cierre-trazable/ingenieria-inversa/inventario.json`.

Los archivos Python/JSX/JS/CSS implementan el producto. SQL fijo se distribuye en 46 recursos por adaptador; migraciones y semillas se conservan en `database/`. Se empaquetan cinco joblib, configuración del modelo y DOCX base. `.env`, venv, node_modules, build y originales académicos no forman parte del paquete. El inventario se obtiene de archivos/AST/OpenAPI, no de nombres de tecnologías en el informe.
