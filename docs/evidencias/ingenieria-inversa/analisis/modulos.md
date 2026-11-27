> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Módulos reconstruidos

`adapters/in/controllers` y schemas: frontera HTTP; `adapters/in/web`: interfaz y sesión. `application/use_cases`: orquestación y autorización; `application/ports`: contratos de persistencia, IA, documentos, exportación y transacciones. `domain`: entidades, valores y reglas. `adapters/out`: PG/memoria, IA, extracción/Storage y exportación. `infrastructure`: composición, configuración y proveedores Auth.

El módulo nuevo de revisión reutiliza Informe/VersionInforme y unidad de trabajo; añade un puerto y repositorios de eventos. El decorador InformeAuditado registra creación de versiones dentro de la misma transacción. SQL fijo vive en recursos por adaptador y los identificadores del guardado genérico siguen compuestos con psycopg.sql.
