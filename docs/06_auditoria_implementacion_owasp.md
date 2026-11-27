# Verificación de seguridad

| Hallazgo | Evidencia real | Estado |
|---|---|---|
| OW-01 | `test_cache_y_logs_no_incluyen_token_ni_identificador`, middleware | Corregido localmente; proxy externo pendiente |
| OW-02 | Test rechaza HTTP antes de enviar clave; tests de Storage privado existentes | Corregido en código; bucket real pendiente |
| OW-03 | Tests CORS/Swagger; valores por entorno y documentación de orígenes | Corregido localmente; configuración desplegada pendiente |
| OW-04 | npm producción y completo sin avisos en consulta actual; pip-audit runtime sin avisos tras actualizar; ambos SBOM | Corregido en versiones consultadas; no garantiza ausencia futura ni vulnerabilidades desconocidas |
| OW-05 | Logs de rechazo sanitizados y eventos crear/editar/revisar/exportar; PG impide UPDATE/DELETE de eventos | Parcial: colector, alertas, retención y responsables externos pendientes |
| OW-06 | Contratos Auth con dobles; perfiles/roles y permisos PG aislados; cookies cross-site probadas por cabeceras | Parcial: no se probaron Supabase compartido, navegador real cross-site ni revocación del proveedor |
| OW-07 | 750 llamadas medidas, límites existentes conservados, fallo/reserva/concurrencia probados | Parcial: la carga usa dobles costosos; no se acordaron cuotas ni SLO institucionales |
| OW-08 | Verificación de seis huellas previo a load; replay CSV/notebook y clones en memoria coincidentes | Parcial: procedencia técnica contrastada; autoría de etiquetas, custodia y protección del pipeline no certificadas |

Puntaje académico provisional de cobertura local, escala original 0/1/2: A01=1, A02=2, A03=2, A04=1, A05=2, A06=2, A07=1, A08=1, A09=1, A10=2: **15/20**. No es una certificación OWASP, una prueba de penetración ni un resultado de producción. Los avisos de dependencias son resultados del registro a la fecha de ejecución.

Regresión: consulte `verificacion-final-*/checks.json` y logs; las corridas fallidas quedan preservadas junto a las correcciones. Las nuevas pruebas no relajan las aserciones de permisos, atomicidad o citas existentes.
