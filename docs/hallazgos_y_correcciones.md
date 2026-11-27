# Actualización de hallazgos de cierre

Base `main` **7359a67**. Los **3 PMV y 10 HU están aceptados para el cierre académico por instrucción del usuario**. La validación institucional externa queda fuera del alcance. Las pruebas omitidas conservan ese estado. No se modifican pilotos, predictor, RAG, HU-IA-04, esquema ni documentos académicos originales.

C-01…C-12 se documentan en [matriz de observaciones](MATRIZ_OBSERVACIONES_CIERRE.md). Se cerraron las guardias de imports/SQL y las cabeceras ZAP confirmadas. No se encontraron infracciones productivas de capas/SQL que justificaran tocar adaptadores. Understand permanece bloqueado. Las observaciones institucionales de la tabla histórica siguiente están fuera de esta misión, no bloquean el cierre académico.

---

## Antecedente conservado (corte anterior)

# Hallazgos históricos y correcciones actuales

Fuente: evaluación histórica del 20/11/2026, pp. 25–28. Los estados se refieren al candidato local, no reescriben la evaluación original ni certifican producción.

| ID | Hallazgo / actuación actual | Evidencia | Estado |
|---|---|---|---|
| H-02 | Evaluación externa del predictor: se reconstruyó test 30 del CSV200 y se evaluó CSV60 adicional; no se acredita independencia institucional | `ml/procedencia-particiones-validacion.json`, script auditor | **Parcial**; corpus real independiente pendiente |
| H-03 | Memorando no está en clases entrenadas. Selección humana y plantilla piloto complementaria; aviso en UI. No se fabricó una clase nueva | Artefactos, semilla complementaria, `test_cierre_pmv1.py`, catálogo/frontend | **Parcial**: uso manual implementado; cobertura predictiva no implementada deliberadamente al conservar modelos |
| H-04 | RAG sintético reproducido; además PDF MINAM local, pp. 23–32, 26 fragmentos, 8 consultas | `rag-minam-real.json`: Hit@1 4/6, Hit@k 5/6, negativas 2/2 | **Parcial**: corpus pequeño, ground truth técnico por página y sin revisión humana institucional; MINAM-04 sin recuperación |
| H-05 | Auth/Storage, perfiles/roles, HTTPS y cookies configurables; revocación de perfil en contratos | `test_auth.py`, `test_perfil_postgres.py`, `test_pmv2.py`, seguridad | **Parcial**: Supabase/RLS/bucket/revocación del proveedor y navegador cross-site reales bloqueados por falta de entorno autorizado |
| H-07 | PMV3 de una etapa, controles backend, versiones/eventos, auditoría y Word/PDF aprobado | `test_pmv3*.py`, frontend revisión, migración nueva | **Verificado local**; aceptación institucional pendiente |
| H-09 | Informes FURPS/OWASP y evidencia de ejecución generados | `01_...` a `07_...`, logs y SBOM | **Parcial**: Understand no disponible/licencia no acreditada; no se lo sustituye nominalmente |
| H-10 | Manifiestos unificados por pyproject, lock runtime y entrada compatible PMV2; wheel instalado limpio | `empaquetado/`, 46 SQL empaquetados | **Verificado Windows**; Linux pendiente |
| H-11 | Auditorías npm/Python y SBOM reales; resoluciones compatibles corregidas | `dependencias/*despues*`, SBOM | **Verificado en consulta actual**; monitoreo periódico pendiente |
| H-12 | Motivos/justificaciones por sección, citas/snapshots y fuentes inaccesibles; atribución literal si LLM omite una referencia aportada | `respaldo.py`, revisión, test atribución, PMV3-RAG | **Parcial**: software registra decisión; no hay certificación semántica/jurídica ni evaluadores institucionales nuevos |
| H-13 | Se localizaron CSV200, CSV60 y notebooks. Replay 140/30/30 coincide en vocabulario/IDF y coeficientes; umbral 0,25; hashes conservados | Auditoría ML agregada sin publicar originales; diferencias coeficientes ≤3e-14 | **Verificado contraste técnico**, **parcial procedencia formal**: etiquetas/custodia/independencia no certificadas |
| H-14 | 750 llamadas HTTP con IDs únicos y métricas; pruebas reales Ollama y PG separadas | Carga, recursos y logs de verificación | **Parcial**: no capacidad productiva de proveedores reales, disponibilidad de despliegue ni línea base municipal |

Otros hallazgos: H-01 (formato de paper), H-08 (cierres Scrum verificables), H-15/H-20 (seis frente a siete atributos), H-17/H-18 (diseño frente al stack real) se abordan en la matriz de correcciones académicas. H-06 (móvil/imágenes) no autoriza módulos ajenos al alcance. H-16 (CI): workflow implementado con acciones e imagen fijadas por hash, permisos de lectura, sin secretos ni despliegue; sintaxis validada localmente, ejecución GitHub pendiente de publicación autorizada.

## Defectos confirmados durante la ejecución

| ID local | Disparador y corrección | Prueba/evidencia |
|---|---|---|
| N-01 | Clase Riesgo de Desastres sin correspondencia institucional producía error total: sugerencia de área queda vacía, con aviso y corrección humana obligatoria | `test_area_sin_correspondencia_no_inventa_destino_y_exige_correccion` |
| N-02 | Plantilla técnica antigua declaraba ausencia de resultados en detalle, pero no activaba el guard de pendientes: se reconoce la declaración explícita. Selector Sin resultados prevalece sobre notas | `test_cierre_pmv1.py`; primera corrida real fallida y regresión real aprobada |
| N-03 | JSONB reordenaba claves y la API no presentaba el orden del snapshot: DTO ordena sin mutar datos ni eliminar extras | `test_orden_presentacion.py`; verificación final-01 conserva el fallo original |
| N-04 | LLM omitió identificador E1 de referencia aportada: si falta un identificador explícito se añade atribución literal de los datos fuente, marcada no corroborada | `test_atribucion_fuente.py`; final-02 conserva el fallo; no se relajan tests existentes |
| N-05 | Historial previo sin eventos podía aparecer como BORRADOR reconstruido: ahora `NO_REGISTRADO` | Prueba PG de historial antiguo |
| N-06 | SameSite=strict fijo no servía para sesión entre los sitios informados: opción configurada con Secure obligatorio para none y CSRF conservado | `test_cookie_cross_site_configurable_requiere_https_y_conserva_csrf` |
| N-07 | Instalación editable PEP660 con namespaces fallaba en importlib.resources/Python3.11: paquetes regulares para persistencia/documentos | Suite en venv limpio: fallo preservado y345 aprobadas/21 omitidas tras la corrección; recursos SQL legibles fuera del cwd |
| N-08 | Un informe antiguo sin creado_por no debe permitir autorrevisión al propietario con varios roles | Prueba específica de permisos históricos; encabezado y texto adicional antiguo visibles antes de decidir |
| N-09 | Hash raw del JSON de configuración variaba entre LF/CRLF por Git: normalización solo de saltos para JSON; joblib permanece binario | Prueba de ambas variantes sin modificar modelos originales |
| N-10 | Verificador PMV2 antiguo sobrescribía resultados y fijaba fecha de octubre: ahora crea directorio único con fecha real de Lima | Dos invocaciones simuladas preservan el histórico; no se presentan como ejecuciones de pytest |

Los fallos de Ollama pueden seguir siendo errores controlados sin guardado; las reglas no garantizan ausencia universal de alucinaciones. Ningún registro de aprobación del arnés acredita una revisión humana real.
