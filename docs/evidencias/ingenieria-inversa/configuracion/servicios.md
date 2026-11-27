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
