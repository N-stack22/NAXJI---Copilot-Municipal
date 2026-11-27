# Prompt 3 — Proveedores e infraestructura

Main **4f4d294**, corte 27/11/2026. [Container](../../../../src/infrastructure/configuration/container.py) compone proveedores; los contratos están en [aplicación](../../../../src/application/ports/output/). El grafo estático se entrega en [dependencias-rutas.csv](../../understand/dependencias-rutas.csv), sin atribuirle llamadas HTTP que no resuelve.

| Proveedor/herramienta | Evidencia y límite |
| ---| ---|
| PostgreSQL/pgvector | Clúster desechable loopback y servicio CI; no Supabase compartido. [Fixtures](../../../../tests/test_pmv2_postgres.py), [CI](../../../../.github/workflows/ci.yml). |
| O llama | HTTP síncrono para qwen2.5:7b y bge-m3:567m, con timeouts. [Evidencias reales opt-in](../../cierre-trazable/ollama-real/), separadas de dobles de carga/CI. |
| Supabase Auth/Storage | Adaptadores REST con contratos y permisos comprobados localmente; sesiones, revocación y políticas del destino externo no se afirman verificadas por esta documentación. |
| Railway/Cloudflare Pages | Destinos informados y configuración preparada:[railway.toml](../../../../railway.toml), [public/_headers](../../../../public/_headers), [guía](../../../PREPARACION_DESPLIEGUE.md). No nueva promoción ni escaneo remoto. |
| ZAP 2.17.0 | Ejecutado antes/después en red Docker local aislada; [reportes](../../cierre-seguridad-20261126/zap/). El diagnóstico antiguo de ausencia de ZAP está superado. |
| Understand 8.1.1269 | C-06 cerrada:[CSV/HTML/diagramas](../../understand/README.md), 0 errores/224 advertencias de resolución documentadas. La licencia es operativa; no se exportan códigos de licencia. |
| Carga 750 | [HTTPX/Python](../../cierre-seguridad-20261126/carga-750-final/resultado.json), 750 respuestas esperadas/0 errores inesperados. No se atribuye a JMeter, k 6 o Sonar ni a una prueba de proveedores productivos. |

Qdrant, TypeScript y Event-Driven fueron alternativas evaluadas, no proveedores finales. Un registro SQL de eventos de revisión no es un broker.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Dependencias de infraestructura

PostgreSQL/pgvector se ejecutó en Docker desechable, puerto loopback 15432, rol de pruebas naxji_step3. Cada fixture creó una base aleatoria independiente. Ollama local respondió con qwen2.5:7b y bge-m3:567m en las integraciones reales.

Railway y Cloudflare Pages son destinos informados por el usuario, sin despliegue ni verificación operativa remota en esta misión. Supabase compartido no se utilizó. No se dispone de Understand/JMeter/ZAP/Sonar en PATH ni de licencia acreditada de Understand; k6 está disponible pero el ensayo de 750 se ejecutó con HTTPX/Python, sin atribuirle el nombre de otra herramienta.
