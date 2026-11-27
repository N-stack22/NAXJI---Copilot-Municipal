> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Detección arquitectónica

| Patrón | Evidencia | Confianza |
|---|---|---|
| Puertos/adaptadores | application/ports, casos de uso e implementaciones out | Alta |
| Capas | domain, application, adapters, infrastructure y pruebas AST | Alta |
| Clean Architecture estricta | Dominio/aplicación desacoplados; algunos adaptadores consumen configuración de infraestructura | Parcial/media |
| Monolito modular | Un backend FastAPI compuesto por Container | Alta |
| MVC | Controladores HTTP y entidades; React organiza la vista con componentes | Parcial; no patrón principal |
| Microservicios de negocio | No se observan servicios internos autónomos; Ollama es un proveedor separado | No demostrado |
| Eventos/broker/workers | No hay infraestructura de broker/workers implementada | Ausente en el código; propuesta documental |

No se infiere una arquitectura de eventos a partir de las reservas de generación o del registro de auditoría.
