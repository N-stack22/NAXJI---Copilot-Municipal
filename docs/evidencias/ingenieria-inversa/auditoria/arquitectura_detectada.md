# Prompt 2 — Detección arquitectónica

Main **4f4d294**, corte 27/11/2026. Patrón principal comprobado: **arquitectura hexagonal** en un backend modular, con frontend React separado. No se declara una implementación nueva de Clean Architecture estricta.

| Capa/patrón | Evidencia del código | Evaluación |
| ---| ---| ---|
| Dominio | [entities, value_objects, services](../../../../src/domain/) | Sin dependencias resueltas hacia aplicación/adaptadores/infraestructura en las reglas examinadas. |
| Aplicación | [use_cases](../../../../src/application/use_cases/), [ports](../../../../src/application/ports/) | Coordina negocio y depende de contratos/dominio; no importación directa de proveedores según guardias y grafo propios resueltos. |
| Entradas | [controllers/schemas](../../../../src/adapters/in/), [web](../../../../src/adapters/in/web/) | FastAPI/React constituyen fronteras; no son el núcleo del dominio. |
| Salidas | [adapters/out](../../../../src/adapters/out/) | Implementan ABC/Protocol de PG, IA, Storage, extracción y exportación. |
| Composición | [Container](../../../../src/infrastructure/configuration/container.py), [create_app](../../../../src/main.py) | Inyección explícita; algunos adaptadores consumen configuración de infraestructura. No hay pureza de dependencias exigida entre todas las capas exteriores. |
| Unidad de trabajo | [PostgresUnidadTrabajo](../../../../src/adapters/out/persistence/postgres.py), [UnidadTrabajo](../../../../src/application/ports/output/unidad_trabajo.py) | Transacciones/savepoints y bloqueos; no broker ni un microservicio de negocio por caso de uso. |

Comprobaciones existentes: [guardias 110 módulos/599 imports](../../cierre-seguridad-20261126/arquitectura-release/resultado.json) y [Understand:423 relaciones propias, 0 infracciones evaluadas del núcleo](../../understand/verificacion-hexagonal.json). Son herramientas distintas; las dependencias dinámicas no resueltas quedan como límite explícito.

[Diagrama nativo de dependencias](../../understand/diagramas/hexagonal-dependencias.svg), [reconstrucción del flujo](../analisis/arquitectura_real.md) y [evaluación](../analisis/calidad_arquitectura.md). Qdrant, TypeScript y Event-Driven fueron alternativas evaluadas; no constituyen el stack final.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

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
