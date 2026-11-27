# Diagnóstico OWASP Top 10:2021

Se adopta 2021 porque es la edición exigida por la guía original. Revisión de código, límites HTTP, transacciones y dependencias del candidato; sin escaneo de servicios compartidos. Los puntajes históricos 10/20 y 14/20 no se registran como resultados actuales.

| Categoría | Evidencia / exposición contrastada | Riesgo |
|---|---|---|
| A01 Control de acceso | Propiedad/perfil/área en servidor, filtros antes del ranking; faltaba revisión persistente PMV3 | Alto si no se comprueban roles y RLS reales |
| A02 Criptografía | Auth/DB exigían TLS; Storage permitía HTTP; faltaba no-store en solicitudes/contexto | Alto para una clave privada mal configurada |
| A03 Inyección | Parámetros separados, identificadores seguros; archivos/citas validados; documentos pueden contener prompt injection | Medio residual: el LLM no acredita validez del contenido |
| A04 Diseño inseguro | Límites de archivos/contexto/reservas; sin cuotas operativas acordadas ni capacidad real medida | Medio por consumo de recursos |
| A05 Configuración | CORS admitía comodín con credenciales; documentación API no era desactivable | Medio; no se presume que producción tuviera esa configuración |
| A06 Componentes | Auditoría npm inicial: producción 1 alta; árbol completo 5 altas/3 moderadas. Candidato Python con certifi/Pillow vulnerables | Alto; alcance distinto entre navegador, build y servidor |
| A07 Autenticación | Verificación remota, perfil fresco y cookies; SameSite=strict fijo no permitía renovar entre los dominios informados | Medio; navegador y Auth institucional por verificar |
| A08 Integridad | Hash documental y lockfile; joblib se deserializaba sin verificar huella | Medio: artefactos de confianza y protección del pipeline necesarios |
| A09 Registro | Logging de errores sin eventos explícitos 401/403/429 ni auditoría de negocio PMV3 | Medio; alertas/retención no demostradas |
| A10 SSRF | URLs configuradas en servidor, sin redirecciones; procedencia documental es texto | Bajo en lo inspeccionado; reglas de salida de red pendientes |

Auditorías JSON antes/después y SBOM: `evidencias/cierre-trazable/dependencias/`. El informe Python inicial corresponde al entorno candidato con dependencias PDF, no se atribuye retrospectivamente a main.
