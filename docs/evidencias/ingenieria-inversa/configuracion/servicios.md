# Prompt 4 — Servicios y ejecución por entorno

Main **4f4d294**, corte 27/11/2026. [Container](../../../../src/infrastructure/configuration/container.py) selecciona memory/postgres de forma explícita; PostgreSQL no cae silenciosamente a memoria. [Settings](../../../../src/infrastructure/configuration/settings.py), [DatabaseSettings](../../../../src/infrastructure/configuration/database.py) y [RagSettings](../../../../src/infrastructure/configuration/rag.py) validan configuración del backend.

| Entorno/servicio | Función y condición | Evidencia/límite |
| ---| ---| ---|
| Demo memoria | Repositorios yAuth mock, solo demostración | No se presenta como persistencia o identidad institucional. |
| PostgreSQL | Persistencia transaccional, SQL recursos, roles/perfiles | [pruebas PG](../../../../tests/test_pmv3_postgres.py) yCI usan bases aisladas; no se migran servicios compartidos. |
| Supabase | Auth REST con perfil PG y Storage privado para RAG | [Auth](../../../../src/infrastructure/auth/supabase.py), [Storage](../../../../src/adapters/out/documents/almacen_supabase.py); operación externa queda fuera del cierre académico. |
| O llama | Generación qwen2.5:7b, embeddings bge-m3:567m | Proveedor HTTP configurable con timeouts; reales opt-in históricos no se confunden con dobles. |
| RAG | RequierePG, vector(1024), Storage, extractor y embeddings | Bandera explícita y misma revisión de procesamiento; sin broker ni worker. |
| PMV 3 | Revisión de una etapa, historial, auditoría y exportación a probada | Bandera explícita y tabla revision_eventos; no segunda aprobación APROBADOR. |
| Diagnóstico | `/health` liveness;`/ready` lectura privada para ADMINISTRADOR | No acredita permisos operativos, capacidad ni aceptación del destino. |

El [preflight](../../../../deploy/preflight.py) es offline y la [guía de despliegue](../../../PREPARACION_DESPLIEGUE.md) separa configuración preparada de servicios reales. No se inicia ni se prueba producción para cerrar estos prompts.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Reconstrucción de servicios

| Servicio | Integración comprobada | Lo que queda pendiente |
|---|---|---|
| PostgreSQL/pgvector | Real, local, desechable | RLS/grants del entorno institucional |
| sklearn | Artefactos reales, huellas y replay de particiones | Custodia/etiquetas/validación institucional independiente |
| Ollama generación y embeddings | Modelos reales en pruebas opt-in | Servicio estable privado y capacidad desplegada |
| Supabase Auth | Contratos con transporte simulado y perfiles PG | Sesiones/revocación reales |
| Storage | Bucket privado/HTTPS por contratos; almacén doble en recorridos aislados | Bucket/políticas reales autorizados |
| Word/PDF | Contenido guardado y pruebas sin inferencia al exportar | Aprobación de membrete/formato institucional |

`/ready` es una lectura diagnóstica privada; `/health` conserva liveness. No confundir disponibilidad con autorización efectiva o aceptación.
