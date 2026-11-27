# Plan de remediación OWASP

| ID | Prioridad / componentes | Mitigación y validación | Rollback compatible |
|---|---|---|---|
| OW-01 | Media / middleware | No-store en solicitudes/contexto/revisión/auditoría; comprobar contratos y salud | Conservar no-store en proxy si se revierte aplicación |
| OW-02 | Alta / Storage | Rechazar HTTP antes de utilizar clave; probar bucket público, subida/lectura y fallos con transporte simulado | Restaurar URL HTTPS válida o pausar carga |
| OW-03 | Media / Settings/API | CORS explícito; bandera documentación; validar endpoints y origen | Restaurar lista concreta aprobada, sin comodín |
| OW-04 | Alta / dependencias | Actualizaciones compatibles npm, mínimos corregidos certifi/Pillow; npm ci, pip-audit, SBOM y suites | Revertir locks/manifiesto juntos; detener promoción vulnerable |
| OW-05 | Media / logs y auditoría | Método/plantilla/estado sin token/ID en logs de rechazo; eventos inmutables PMV3 | Ajustar colector/retención; conservar historial de negocio |
| OW-06 | Alta / entorno institucional | Validar Auth, revocación, bucket, TLS, RLS y cookies con cuentas de prueba autorizadas | No habilitar flujo si no puede verificarse el ámbito efectivo |
| OW-07 | Media / capacidad | Medir primero; acordar cuotas por usuario/costo con operador | Detener carga y conservar límites actuales; no imponer cuotas arbitrarias |
| OW-08 | Media / modelos y pipeline | Huellas antes de joblib, procedencia/particiones y SBOM; comparar artefactos sin reemplazarlos | Restaurar paquete confiable íntegro; no aceptar joblib de usuarios |

La sesión entre sitios usa SameSite configurable, con Secure obligatorio para `none`, y conserva cabecera no simple/origen permitido contra CSRF. La configuración de cookies de terceros del navegador sigue siendo una condición externa. No se programó un despliegue ni se crearon secretos.
