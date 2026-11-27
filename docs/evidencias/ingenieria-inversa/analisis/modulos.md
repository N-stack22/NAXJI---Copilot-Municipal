# Módulos y responsabilidades vigentes

Main **4f4d294**, corte 27/11/2026. [InventarioAST](../cierre-documental-20261127/inventario-fuente.json) y [hashes](../cierre-documental-20261127/fuentes-sha256.json) permiten verificar el recorrido sin cambiar producto.

| Ruta | Responsabilidad y contrato real |
| ---| ---|
| [domain](../../../../src/domain/) | 18 módulos; entidades, valores, enumeraciones y políticas. [Prompt 8 completo](dominio.md). |
| [application](../../../../src/application/) | 31 módulos; puertosABC/Protocol, DTO y casos de uso; no repositorios dentro de dominio. |
| [adapters](../../../../src/adapters/) | 52 módulosPython másWeb; controllers/schemas ysalidasPG/memoria, IA, documentos/exportación. |
| [infrastructure](../../../../src/infrastructure/) | 8 módulosPython; configuración, composición yAuth; artefactosML son recursos. |
| [main](../../../../src/main.py) | Bootstrap, handlers, middleware, CORS y registro de rutas; no una capa de dominio. |

[Container](../../../../src/infrastructure/configuration/container.py) selecciona UoW/repositorios, inyecta predictor/generador y activa RAG/PMV 3 según configuración. [InformeAuditado](../../../../src/adapters/out/persistence/informe_auditado.py) decora el repositorio de informes y registra CREAR_VERSION en la misma UoW. [SQL recursos](../../../../src/adapters/out/persistence/sql/) contiene 46 consultas;`save()` conserva composición de identificadores con psycopg.sql.

El inventario 110 módulos/599 imports de [guardias](../../cierre-seguridad-20261126/arquitectura-release/resultado.json) nose suma alas 423 relaciones resueltas por [Understand](../../understand/dependencias-rutas.csv): son mediciones distintas. La [reconstrucción arquitectónica](arquitectura_real.md) distingue importaciones de flujo de ejecución.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Módulos reconstruidos

`adapters/in/controllers` y schemas: frontera HTTP; `adapters/in/web`: interfaz y sesión. `application/use_cases`: orquestación y autorización; `application/ports`: contratos de persistencia, IA, documentos, exportación y transacciones. `domain`: entidades, valores y reglas. `adapters/out`: PG/memoria, IA, extracción/Storage y exportación. `infrastructure`: composición, configuración y proveedores Auth.

El módulo nuevo de revisión reutiliza Informe/VersionInforme y unidad de trabajo; añade un puerto y repositorios de eventos. El decorador InformeAuditado registra creación de versiones dentro de la misma transacción. SQL fijo vive en recursos por adaptador y los identificadores del guardado genérico siguen compuestos con psycopg.sql.
