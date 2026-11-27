# Auditoría OWASP Top10:2021

Base `main` **7359a67**. Los **3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Las pruebas omitidas conservan ese estado. No se modifican pilotos, predictor, RAG, HU-IA-04, esquema ni documentos académicos originales.

Se utiliza **OWASP 2021**, como exige el encargo. El escaneo real es ZAP 2.17.0 contra un laboratorio Docker interno; nunca producción. Frontend: spider/pasivo sobre build. API: OpenAPI/activo con identidad ficticia de funcionario; memoria y dobles. No demuestra seguridad de PostgreSQL/Supabase/Ollama productivos.

| Categoría2021 | Evidencia actual | Límite conservado |
|---|---|---|
| A01 Acceso | Regresiones de propietario/rol/área y snapshots; API escaneada con token de prueba | RLS y cuentas institucionales fuera de alcance |
| A02 Criptografía | Contratos TLS/cookies existentes; solo HTTP dentro de red local aislada de escaneo | No se certifica TLS del edge ni del proveedor |
| A03 Inyección | SQL parametrizado/psycopg.sql intactos; guardia de SQL fijo y escaneo activo de API | API ZAP usa repositorio en memoria; no prueba inyección SQL contra PG ni prompt injection real |
| A04 Diseño | Límites, reservas, rollback y flujos de revisión existentes sin cambios | No se inventan cuotas ni requisitos |
| A05 Configuración | Se confirmaron CSP/marcos/nosniff ausentes en el laboratorio | Remediación y reescaneo explícitos |
| A06 Componentes | Locks/SBOM y auditorías guardadas en base; npm ci actual sin avisos | No es auditoría continua de OS ni garantía futura |
| A07 Autenticación | Token ficticio verificado en /auth/me200 durante ZAP; contratos y permisos cubiertos | No credenciales/proveedor real ni UI cross-site autenticada |
| A08 Integridad | Huellas de modelos intactas, wheel instalado y recursos empaquetados | Procedencia institucional externa no se amplía |
| A09 Logs | Logs de pruebas/ZAP/CI conservados; eventos inmutables y rechazo simulado existentes | Sin afirmar monitoreo operativo o actas |
| A10 SSRF | Red Docker internal sin salida y sin servicios externos; URLs de configuración conservadas | No pentest de infraestructura productiva |

La primera corrida `zap/antes/` quedó exploratoria: el filtro inicial del header demo no autenticó la API. La comparación válida usa `antes-02` y `despues`, ambas con /auth/me200 y cobertura registrada. No se esconde esa limitación.

Evidencia actual: [resultados](RESULTADOS_CIERRE.md), [observaciones cerradas y pendientes](MATRIZ_OBSERVACIONES_CIERRE.md), [12 entregables](INDICE_12_ENTREGABLES.md) y [preparación de despliegue](PREPARACION_DESPLIEGUE.md). Los logs históricos de `evidencias/cierre-trazable/` se conservan; no se suman suites repetidas para inflar resultados.
