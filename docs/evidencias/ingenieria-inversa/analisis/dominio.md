# Prompt 8 — Reconstrucción del dominio de NAXJI

Vigente al **27/11/2026**, sobre `main` **4f4d294f615cf0285d19f23d0f2aabbf1ee339d1**. Reconstrucción por lectura directa de código; no introduce entidades, patrones, reglas ni HU nuevas. Los tres PMV y diez HU están completos dentro del alcance académico acordado. La validación institucional externa queda fuera de ese alcance.

Fuentes verificables: [inventario AST de clases, campos y métodos](../cierre-documental-20261127/inventario-fuente.json), [huellas de los 149 archivos propios](../cierre-documental-20261127/fuentes-sha256.json), [diagramas UML textuales](diagramas_dominio.md) y [matriz de los doce prompts](../../../INDICE_12_ENTREGABLES.md). Las huellas coinciden con las fuentes del análisis real de [Understand, C-06 cerrada](../../understand/README.md); no se atribuye este inventario AST a esa herramienta.

## 1. Vocabulario y entidades observadas

Las clases son dataclasses, con identidad UUID donde se indica. El nombre del directorio `entities` no prueba por sí solo que una clase sea una entidad DDD; se describe la forma efectiva del código.

| Archivo real | Clases | Identidad, datos y relaciones observadas |
| ---| ---| ---|
| [solicitud.py](../../../../src/domain/entities/solicitud.py) | `Solicitud`, `SolicitudValor` | Solicitud tiene `id`, `usuario_id`, asunto, referencias opcionales a tipo/plantilla/áreas, estado, fechas y lista de valores. Cada valor tiene su propio `id`, `solicitud_id`, `campo_plantilla_id` y `valor: Any`. |
| [informe.py](../../../../src/domain/entities/informe.py) | `Informe`, `VersionInforme` | Informe identifica solicitud, plantilla y creador; conserva título, estado y versiones. Cada versión tiene `id`, `informe_id`, número, contenido JSON, origen, autor, metadatos IA y snapshots opcionales de título, estructura y sustento. |
| [plantilla.py](../../../../src/domain/entities/plantilla.py) | `Plantilla`, `CampoPlantilla` | Plantilla con `id`, tipo, área opcional, versión, actividad, campos, secciones de salida y formato. Campo con `id`, `plantilla_id`, clave, etiqueta, tipo de dato, obligatoriedad, orden y configuración. Un campo de entrada no es una sección del informe. |
| [prediccion_contexto.py](../../../../src/domain/entities/prediccion_contexto.py) | `PrediccionContexto`, `NormativaPredicha` | Predicción con `id`, solicitud, tipo/área sugeridos, confianzas, modelo/versión, parámetros, resultado y autor/fecha de validación. Las propuestas normativas tienen `id`, `normativa_id`, confianza, orden y aceptación humana opcional. |
| [catalogo.py](../../../../src/domain/entities/catalogo.py) | `TipoInforme`, `AreaMunicipal`, `Normativa` | Dataclasses congeladas con UUID. Área admite `area_padre_id`; normativa registra código/título, actividad, tipo, número, fechas, URL y descripción. Tener URL o fecha no acredita por sí mismo aplicabilidad jurídica. |
| [correspondencia_normativa.py](../../../../src/domain/entities/correspondencia_normativa.py) | `CorrespondenciaNormativa` | Relación curada entre etiqueta temática y objeto `Normativa`; no declara un UUID propio. Registra verificación, fuentes, fecha, ámbito, vigencia, justificación y actividad. `elegible()` y `evidencia()` implementan su contrato. |
| [documento.py](../../../../src/domain/entities/documento.py) | `Documento` | UUID, propietario, ámbito/área, título, procedencia, nombre/tipo/tamaño/hash, ubicación, estado, error, intento/reserva, revisión de procesamiento y número de fragmentos. No incluye una lista de objetos fragmento. |
| [usuario_actual.py](../../../../src/domain/entities/usuario_actual.py) | `UsuarioActual` | Snapshot congelado de identidad/perfil: UUID, `frozenset[Rol]`, área, activo y datos administrativos opcionales. Tiene identidad; su inmutabilidad no lo convierte en un objeto de valor sin identidad. |

No existe una clase de dominio `Fragmento`, `Cita`, `EventoRevision`, `EncabezadoDocumento` ni `AgregadoRaiz`. Los fragmentos, citas y eventos se transportan como diccionarios; sus tablas o contratos no se presentan como clases inexistentes. Los UUID son tipos de biblioteca, sin wrappers propios como `SolicitudId`.

## 2. Objetos de valor, enumeraciones y DTO

| Elemento real | Ubicación y alcance |
| ---| ---|
| `SeccionSalida` | [seccion_salida.py](../../../../src/domain/value_objects/seccion_salida.py): dataclass congelada con `clave`, `titulo`, `obligatoria`; objeto de valor sin UUID propio y validación en `__post_init__`. |
| `EstadoSolicitud` | [estado_solicitud.py](../../../../src/domain/value_objects/estado_solicitud.py): enum de los cinco estados de solicitud. No es una máquina de estados independiente. |
| `EstadoInforme`, `ResultadoValidacion`, `OrigenVersion`, `TipoDato`, `Rol` | [estados.py](../../../../src/domain/value_objects/estados.py): enumeraciones compartidas, no entidades con repositorio. |
| Encabezado administrativo | [encabezado_documento.py](../../../../src/domain/value_objects/encabezado_documento.py): diccionario y funciones `crear_encabezado`, `datos_oficiales`, `actualizar_datos_oficiales`; no hay clase de encabezado. |
| Estructura y campos piloto | [estructura_piloto.py](../../../../src/domain/value_objects/estructura_piloto.py), [fuentes_piloto.py](../../../../src/domain/value_objects/fuentes_piloto.py): funciones que construyen `SeccionSalida`/`CampoPlantilla`, no fábricas abstractas ni nuevos tipos DDD. |
| `DatosSolicitud` | [puerto de entrada](../../../../src/application/ports/input/solicitud_use_case.py): DTO congelado de aplicación; no pertenece al dominio. |
| `NormaConfirmada`, `ContextoConfirmado`, `ResultadoBorrador` | [contrato de generación](../../../../src/application/ports/output/generador_borrador.py): DTO congelados de aplicación. Contexto tiene IDs, denominaciones, normas y fuentes; resultado tiene contenido, modelo, versión de prompt y citas. No son entidades persistidas con repositorio propio. |

`VersionInforme` es una dataclass mutable. La conservación del historial se obtiene mediante copias/snapshots y escrituras de nuevas versiones, no por `frozen=True` ni por un patrón de event sourcing. Un diccionario JSON de sustento tampoco aporta inmutabilidad de Python por sí mismo.

## 3. Agregados y relaciones

Los siguientes límites se **infieren de composición y contratos de guardado**, no de una clase base DDD ni de anotaciones `AggregateRoot`:

| Raíz observada | Elementos asociados | Evidencia de persistencia y límites |
| ---| ---| ---|
| `Solicitud` | `valores: list[SolicitudValor]` | [SolicitudRepository.guardar](../../../../src/application/ports/output/solicitud_repository.py) guarda solicitudes y valores conservando IDs; el adaptador elimina valores ausentes. Referencias a usuario/catálogos/plantilla son UUID, no objetos embebidos. |
| `PrediccionContexto` | `normativas: list[NormativaPredicha]` | [PrediccionRepository.guardar/ultima](../../../../src/application/ports/output/prediccion_repository.py) guarda predicción y propuestas; `ultima` selecciona el contexto vigente de una solicitud. No se valida cualquier predicción histórica. |
| `Informe` | `versiones: list[VersionInforme]` | [InformeRepository](../../../../src/application/ports/output/informe_repository.py) y [InformeRepositoryPostgres.guardar](../../../../src/adapters/out/persistence/postgres.py): números positivos/no duplicados; inserta versiones no existentes sin reescribir las guardadas. Un informe por solicitud según el contrato y el control de generación. |
| `Plantilla` | `campos` y estructura de salida | [PlantillaRepository](../../../../src/application/ports/output/plantilla_repository.py) solo ofrece lectura/listado; no existe caso de uso de autoría institucional de plantillas. Composición descriptiva, no un agregado editable implementado por este puerto. |
| `Documento` | Filas de fragmentos y revisión de procesamiento | [DocumentoRepository](../../../../src/application/ports/output/documentos.py), [DocumentosPostgres.finalizar](../../../../src/adapters/out/persistence/documentos_postgres.py): finalización atómica de índice por intento; los fragmentos no se cargan dentro de la dataclass Documento. |

Relaciones adicionales: `AreaMunicipal.area_padre_id` permite una jerarquía referencial, pero el dominio no implementa validación de ciclos de áreas. `CorrespondenciaNormativa` contiene una `Normativa`. `SolicitudValor.campo_plantilla_id` identifica el campo de entrada; `Informe.plantilla_id` identifica la plantilla usada y `VersionInforme.secciones_salida` conserva su estructura. Los eventos contienen IDs de informe/versión/usuario en un diccionario; son un registro de auditoría del puerto de aplicación, no un agregado de eventos del dominio.

## 4. Servicios y políticas reales

| Servicio o función | Responsabilidad comprobada |
| ---| ---|
| [`SolicitudService`](../../../../src/domain/services/solicitud_service.py) | `validar`: asunto no vacío. `editable`: solo BORRADOR/LISTA_PARA_GENERAR. `validar_valor`: tipos, fechas ISO, números finitos, booleano estricto y opciones SELECT. `validar_obligatorios`: valores pertenecientes a campos activos y presencia de los obligatorios. |
| [`validar_contenido`](../../../../src/domain/services/informe_service.py) | Contenido objeto JSON; secciones obligatorias con texto no vacío; sección presente de tipo texto; JSON serializable sin NaN. |
| [`secciones_efectivas` y `SeccionSalida`](../../../../src/domain/value_objects/seccion_salida.py) | Estructura explícita de 1–100 secciones, claves únicas y no reservadas; clave válida de hasta 80 caracteres, título no vacío de hasta 150 y booleano estricto. `None` aplica estructura legacy, no equivale a una lista vacía. |
| [`actualizar_datos_oficiales`](../../../../src/domain/value_objects/encabezado_documento.py) | Solo claves administrativas permitidas, texto breve, sin UUID técnicos como denominaciones y fecha ISO o pendiente. Los datos administrativos no los inventa el LLM. |
| [`advertencias_respaldo`, `secciones_revisables`](../../../../src/domain/services/respaldo.py) | HU-IA-04: avisos estructurales por falta de contenido, pendientes, citas/acceso y revisión de vigencia. No verifican automáticamente hechos, validez jurídica ni implicación semántica. |
| [`puede_leer`](../../../../src/domain/entities/documento.py) | Perfil activo con roles y permiso por administración, propiedad, ámbito institucional o coincidencia de área para ámbito AREA. La escritura tiene comprobaciones adicionales en aplicación. |
| [`CorrespondenciaNormativa.elegible`, `fuente_oficial`](../../../../src/domain/entities/correspondencia_normativa.py) | Curación activa/verificada, normativa activa, vigencia permitida, fechas coherentes con hoy, ámbito/justificación y fuentes HTTPS oficiales admitidas. Son criterios técnicos de elegibilidad, no certificación legal. |
| [`ErrorDominio` y subclases](../../../../src/domain/services/errores.py) | `DatosInvalidos`, `NoAutorizado`, `NoEncontrado`, `ConflictoEstado`, `ErrorServicio`, `ErrorGeneracion`; expresan fallos esperados. El mapeo HTTP está en el adaptador/bootstrap. |

`autorizar`, `ServiciosSolicitud`, `GenerarBorrador`, `GestionDocumentos` y `RevisionInformes` son **políticas/orquestadores de aplicación**, no servicios de dominio trasladados conceptualmente de capa. No se encontró un servicio de dominio de aprobación autónomo ni un motor genérico de workflows.

## 5. Reglas de aplicación e invariantes efectivas

| Regla | Implementación que la respalda | Alcance y límite |
| ---| ---| ---|
| Identidad activa, rol de elaboración y propiedad | [autorizar y ServiciosSolicitud.obtener](../../../../src/application/use_cases/servicios_solicitud.py) | Escritura requiere FUNCIONARIO o ADMINISTRADOR; propiedad requerida cuando se proporciona propietario, con excepción administrativa. Los permisos no provienen de la interfaz. |
| Referencias de catálogo activas y plantilla compatible | [ServiciosSolicitud.validar_referencias](../../../../src/application/use_cases/servicios_solicitud.py) | Tipo/áreas activos; plantilla activa del tipo y, si fija área, del destino. Elegir otra plantilla vacía los valores anteriores en [ActualizarSolicitud](../../../../src/application/use_cases/actualizar_solicitud.py). |
| Contexto humano válido antes de generar | [PredecirContexto](../../../../src/application/use_cases/predecir_contexto.py), [ValidarPrediccion](../../../../src/application/use_cases/validar_prediccion.py), [GenerarBorrador._reservar](../../../../src/application/use_cases/generar_borrador.py) | Confianzas finitas 0–1 y referencias conocidas; validación de la última predicción y del asunto vigente; confirmar/corregir contexto y completar obligatorios. RECHAZADA no habilita generar. |
| Curación normativa vigente al confirmar y publicar | [verificar_referencias_normativas](../../../../src/application/use_cases/verificar_referencias_normativas.py) | Revalida correspondencias de `mapeo_normativo_version == 1` y normas seleccionadas; no se atribuye este control a todas las predicciones legacy. |
| Guardado del formulario completo atómico | [GuardarSolicitudCompleta](../../../../src/application/use_cases/guardar_solicitud_completa.py) | Coordina crear/actualizar, valores y obligatorios en UoW; los casos de borrador permiten datos incompletos. No son reglas idénticas. |
| Reserva de generación sin bloqueo durante IA | [GenerarBorrador](../../../../src/application/use_cases/generar_borrador.py) | Reserva PROCESANDO, copia contexto y libera conexión durante inferencia; publica solo si mismo intento/timestamp, plazo, solicitud/plantilla/predicción vigentes y sin informe previo. Fallo o reserva vencida permite recuperación controlada. |
| Edición crea versión y conserva metadatos | [ActualizarBorrador](../../../../src/application/use_cases/actualizar_borrador.py) | Solo BORRADOR y número vigente; conserva metadatos/estructura protegidos, actualiza título/encabezado por sus contratos y agrega versión de origen USUARIO. |
| Acceso documental antes de ranking | [GestionDocumentos](../../../../src/application/use_cases/documentos.py), [buscar.sql](../../../../src/adapters/out/persistence/sql/documentos_postgres/buscar.sql) | Corpus autorizado, INDEXADO y misma revisión; CTE materializada antes de distancia coseno, umbral, orden/límite. Fuentes se vuelven a proteger al leer una versión. |
| Índice documental íntegro por intento | [DocumentosPostgres.finalizar](../../../../src/adapters/out/persistence/documentos_postgres.py) | Bloqueo de fila; intento y reserva válidos; reemplazo de fragmentos/estado en una transacción. Hash de original y cardinalidad de embeddings se verifican en aplicación. |
| Citas y ediciones no equivalen a hechos verificados | [vincular_citas, sustento_editado](../../../../src/application/use_cases/documentos.py) | Fragmento citado debe pertenecer al contexto; edición de pasaje marca TEXTO_MODIFICADO. Los avisos HU-IA-04 permanecen. |
| Revisor del destino y distinto del autor | [RevisionInformes.cargar](../../../../src/application/use_cases/revision_informes.py) | Rol REVISOR, área **igual al destino**, usuario diferente del creador y del propietario de la solicitud. No basta el rol ADMINISTRADOR para decidir. Se corrige la ambigüedad del antecedente que decía «distinto ... del área de destino». |
| Decisión sobre versión vigente y justificación humana | [RevisionInformes.decidir](../../../../src/application/use_cases/revision_informes.py) | Solo EN_REVISION; APROBADO/RECHAZADO con motivo 1–4000 caracteres. Para a probar, justificar exactamente las secciones advertidas; no a probar con fuentes sin acceso. Comprobaciones textuales no prueban revisión institucional externa. |
| Informe/decisión/evento atómicos | [UnidadTrabajo](../../../../src/application/ports/output/unidad_trabajo.py), [PostgresUnidadTrabajo](../../../../src/adapters/out/persistence/postgres.py), [InformeAuditado](../../../../src/adapters/out/persistence/informe_auditado.py) | Mismo contexto transaccional, bloqueo del informe y rollback conjunto. [revision_eventos](../../../../database/migrations/20261126_01_pmv3_revision.sql) impide UPDATE/DELETE por trigger; no hay broker ni event sourcing. |
| Exportación a probada de PMV 3 | [RevisionInformes.exportar](../../../../src/application/use_cases/revision_informes.py) | Usa una versión guardada con último evento decisorio APROBADO, permisos actuales y exportador DOCX/PDF; registra EXPORTAR. No regenera con IA. El contrato previo [ExportarInforme](../../../../src/application/use_cases/exportar_informe.py) conserva exportación de lectura autorizada; no se afirma que todas las rutas legacy exijan aprobación PMV 3. |
| Auditoría administrativa | [RevisionInformes.auditoria](../../../../src/application/use_cases/revision_informes.py), [RevisionRepository](../../../../src/application/ports/output/revision_repository.py) | Solo ADMINISTRADOR; consultas paginadas. No se equipara una lista de eventos con un sistema externo de auditoría certificado. |

Las dataclasses de entidades no validan todas estas condiciones al construirse. Hay invariantes en servicios, casos de uso, repositorios y SQL; no se documenta un «dominio rico» con todas las transiciones encapsuladas en entidades. No se inspeccionó ni modificó una base compartida para afirmar restricciones adicionales a las presentes en los contratos/migraciones versionados.

## 6. Estados y transiciones implementadas

| Modelo | Estados declarados | Transiciones observadas, no flujos inventados |
| ---| ---| ---|
| Solicitud | BORRADOR, LISTA_PARA_GENERAR, PROCESANDO, GENERADA, CANCELADA | Recalcular alterna borrador/lista según contexto y obligatorios. Solo estados editables admiten cancelación manual. Reservar pasa a PROCESANDO; publicación a GENERADA; fallo/vencimiento recupera BORRADOR o LISTA, o GENERADA si ya existe informe. No hay reapertura de GENERADA/CANCELADA. |
| Predicción | PENDIENTE, ACEPTADA, CORREGIDA, RECHAZADA | Una nueva predicción nace pendiente. Validar la última permite aceptar/corregir/rechazar mientras la solicitud sea editable; no exige que su resultado anterior sea PENDIENTE. Cambios de asunto/tipo/destino invalidan su confirmación. No se fuerza un ciclo único ficticio. |
| Informe | BORRADOR, EN_REVISION, OBSERVADO, APROBADO, RECHAZADO, ARCHIVADO | Implementado: BORRADOR→EN_REVISION→APROBADO o RECHAZADO; editar conserva BORRADOR o EN_REVISION según actor y crea versión. OBSERVADO/ARCHIVADO son constantes heredadas sin transición pública implementada; no hay devolución/reapertura ni segunda etapa APROBADOR. |
| Documento | Cadenas SUBIENDO, ERROR_CARGA, CARGADO, PROCESANDO, ERROR_PROCESAMIENTO, INDEXADO | Carga a CARGADO o ERROR_CARGA; reenvío del mismo documento reintenta carga. Procesar CARGADO/error o una revisión diferente reserva PROCESANDO y publica INDEXADO/error. INDEXADO con misma revisión es idempotente. Intento vencido no puede sobrescribir uno nuevo. No existe enum `EstadoDocumento`. |
| Cita/historial | PENDIENTE_REVISION, TEXTO_MODIFICADO, NO_REGISTRADO | Son valores de diccionarios/respuesta histórica, no estados de `EstadoInforme`. NO_REGISTRADO conserva desconocimiento de versiones antiguas sin eventos. |

Los [diagramas de estados](diagramas_dominio.md#estados-de-solicitud) representan estas acciones. Los estados sin flujo se listan expresamente fuera de las flechas para no sugerir funciones inexistentes.

## 7. Puertos y contratos de repositorios

Los puertos se encuentran en **aplicación**, no en dominio. Son clases abstractas o `Protocol`; no se cambian interfaces en esta revisión.

| Puerto real | Operaciones del contrato | Ubicación |
| ---| ---| ---|
| `SolicitudUseCase` | `ejecutar(usuario, datos) -> Solicitud`; `DatosSolicitud` | [input/solicitud_use_case.py](../../../../src/application/ports/input/solicitud_use_case.py) |
| `SolicitudRepository` | `guardar`, `obtener_por_id` | [solicitud_repository.py](../../../../src/application/ports/output/solicitud_repository.py) |
| `PlantillaRepository` | `listar`, `obtener_por_id` | [plantilla_repository.py](../../../../src/application/ports/output/plantilla_repository.py) |
| `PrediccionRepository` | `guardar`, `ultima(solicitud_id)` | [prediccion_repository.py](../../../../src/application/ports/output/prediccion_repository.py) |
| `InformeRepository` | `guardar`, `obtener_por_id`, `obtener_por_solicitud` | [informe_repository.py](../../../../src/application/ports/output/informe_repository.py) |
| `CatalogoRepository` | `tipos_informe`, `areas`, `normativa`, `correspondencias_normativas` (vacío por defecto, sin inferir relaciones) | [catalogo_repository.py](../../../../src/application/ports/output/catalogo_repository.py) |
| `PerfilRepository` | `obtener_usuario(usuario_id, email)` | [perfil_repository.py](../../../../src/application/ports/output/perfil_repository.py) |
| `RevisionRepository` | `registrar(evento)`, `eventos`, `listar`, `auditoria` | [revision_repository.py](../../../../src/application/ports/output/revision_repository.py) |
| `DocumentoRepository` | `crear`, `obtener`, `listar`, `reservar`, `finalizar`, `contar`, `buscar`, `fragmento` | [documentos.py](../../../../src/application/ports/output/documentos.py) |
| `UnidadTrabajo` | `transaccion() -> AbstractContextManager[None]`; commit/rollback y serialización equivalente por adaptador | [unidad_trabajo.py](../../../../src/application/ports/output/unidad_trabajo.py) |
| `ContextPredictor` | `predecir(asunto, solicitud_id) -> PrediccionContexto` | [context_predictor.py](../../../../src/application/ports/output/context_predictor.py) |
| `GeneradorBorrador` | `generar(asunto, plantilla, datos, contexto, instrucciones) -> ResultadoBorrador` | [generador_borrador.py](../../../../src/application/ports/output/generador_borrador.py) |
| `LLMPort` | `generar(prompt, sistema=..., esquema=...) -> str`, propiedad `model` | [llm_port.py](../../../../src/application/ports/output/llm_port.py) |
| `AlmacenDocumentos`, `ExtractorDocumentos`, `Embeddings`, `RecuperadorDocumentos` | `guardar/leer`, `extraer`, `codificar` con modelo/dimensión, `recuperar` | [documentos.py](../../../../src/application/ports/output/documentos.py) |
| `ExportadorInforme` | `exportar(informe, version) -> bytes`, sin inferencia ni escrituras | [exportador_informe.py](../../../../src/application/ports/output/exportador_informe.py) |

No hay un puerto abstracto para cada clase de caso de uso; solo se encontró `SolicitudUseCase` como abstracción de entrada explícita en esa carpeta. Tampoco hay repositorios de fragmento/cita/objeto de valor separados del contrato documental o del informe.

## 8. Casos de uso de los tres PMV

| PMV / HU original | Clases o funciones reales que intervienen | Comportamiento documentado |
| ---| ---| ---|
| PMV 1 HU-001, acceso/perfil | [SupabaseAuth](../../../../src/infrastructure/auth/supabase.py), [PerfilRepository](../../../../src/application/ports/output/perfil_repository.py), [controlador Auth](../../../../src/adapters/in/controllers/auth_controller.py), [usuario](../../../../src/adapters/in/controllers/usuario_controller.py) | Sesión e identidad/perfil; este flujo se implementa en adaptadores/infraestructura, sin inventar una clase `AutenticarUsuario` en use_cases. |
| PMV 1 HU-002, solicitud/formulario | [CrearSolicitud](../../../../src/application/use_cases/crear_solicitud.py), [ActualizarSolicitud](../../../../src/application/use_cases/actualizar_solicitud.py), [GuardarValoresSolicitud](../../../../src/application/use_cases/guardar_valores_solicitud.py), [GuardarSolicitudCompleta](../../../../src/application/use_cases/guardar_solicitud_completa.py), [ConsultarCatalogos](../../../../src/application/use_cases/consultar_catalogos.py), [ObtenerSolicitud](../../../../src/application/use_cases/obtener_solicitud.py) | Captura y edición autorizada, compatibilidad catálogo/plantilla, valores y guardado atómico completo. |
| PMV 1 HU-IA-01, contexto y borrador | [PredecirContexto](../../../../src/application/use_cases/predecir_contexto.py), [ValidarPrediccion](../../../../src/application/use_cases/validar_prediccion.py), [ObtenerContexto](../../../../src/application/use_cases/obtener_contexto.py), [GenerarBorrador](../../../../src/application/use_cases/generar_borrador.py), [ObtenerInforme](../../../../src/application/use_cases/obtener_informe.py), [ActualizarBorrador](../../../../src/application/use_cases/actualizar_borrador.py) | Sugerencia ML confirmada por persona, generación reservada y borrador versionado. Consulta/exportación legacy conserva su contrato. |
| PMV 2 HU-003, documentos | [GestionDocumentos](../../../../src/application/use_cases/documentos.py): `cargar`, `procesar`, `listar`, `obtener`, `original`, `fragmento` | Carga autorizada, extracción, integridad, segmentación, embeddings y publicación atómica de índice. |
| PMV 2 HU-IA-02, recuperación | `GestionDocumentos.recuperar`, `GenerarBorrador` con recuperador opcional | Recuperación por permisos/estado/revisión y presupuesto de contexto; CORPUS_VACIO/SIN_RESULTADOS no se convierten en citas inexistentes. |
| PMV 2 HU-IA-03, fuentes/citas | `vincular_citas`, `sustento_editado`, `GestionDocumentos.proteger`, `ObtenerInforme.proteger` | Snapshots, marcadores por UUID de fragmento y ocultación cuando se pierde acceso. |
| PMV 3 HU-IA-04, advertencias | [advertencias_respaldo](../../../../src/domain/services/respaldo.py), `RevisionInformes.historial/decidir` | Señalar límites y exigir justificación de revisión; no se cambian sus textos ni criterios. |
| PMV 3 HU-004, revisión/decisión | [RevisionInformes](../../../../src/application/use_cases/revision_informes.py): `enviar`, `editar`, `decidir` | Una etapa de revisión por un revisor del área de destino, distinto del creador del informe y del propietario de la solicitud. |
| PMV 3 HU-005, historial/exportación | `RevisionInformes.listar`, `historial`, `exportar` | Historial por versión/eventos y exportación de contenido guardado a probado, sin volver a invocar IA. |
| PMV 3 HU-006, auditoría | `RevisionInformes.auditoria`, `RevisionRepository` | Consulta administrativa paginada, separada de la autorización del revisor. |

Las HU son diez; los doce prompts son entregables de análisis, no doce funcionalidades. El [mapeo funcional ampliado](casos_uso.md) y las [pruebas/capturas existentes](../../../matriz_trazabilidad.md) aportan evidencia de los recorridos sin repetirlos en este cierre.

## 9. Diagramas y límites de los patrones

[UML de clases, estados y secuencia](diagramas_dominio.md) reconstruido manualmente desde las clases/métodos anteriores. Los fuentes `.mmd` están en [diagramas](diagramas/). No se atribuyen a Understand: sus gráficos nativos de dependencias siguen en [su carpeta de evidencias](../../understand/diagramas/).

Patrones ausentes o no acreditados: clase formal de raíz de agregado, repositorio genérico de dominio por entidad, event bus/broker/workers, event sourcing, CQRS con almacenes independientes, servicio de aprobación de dos niveles, motor de workflows y wrappers de identidad/VO para cada campo. Las reservas, `ContextVar`, eventos SQL y un `Protocol` no equivalen a esos patrones. No se implementa nada para completar esta lista.

La lectura de contratos, AST y SQL no certifica despliegue institucional, vigencia jurídica, generalización de ML o revisión humana real. Se conservan las 375 pruebas backend a probadas y 21 optativas omitidas, 55 frontend, 750 llamadas con resultado esperado, ZAP y Understand con sus cortes y límites en [resultados](../../../RESULTADOS_CIERRE.md). Este cierre no modifica código, esquemas, modelos, plantillas ni informe académico.

## Antecedente literal conservado de 4f4d294

El diagnóstico de Understand bloqueado que sigue es histórico y está superado desde C-06. La frase antigua sobre «revisor ... distinto ... del área de destino» era ambigua/incorrecta: el código requiere revisor **de la misma área de destino** y distinto de los autores, como se precisa arriba.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Reconstrucción del dominio

Solicitud contiene valores y referencias de catálogo; Informe contiene VersionInforme; PrediccionContexto contiene NormativaPredicha; Plantilla contiene campos y una lista de SeccionSalida. Documento conserva propietario/ámbito/hash/estado y se relaciona con fragmentos. UsuarioActual es identidad con roles/área/perfil activo.

Reglas: solo el propietario o administrador elabora; contexto confirmado y obligatorios antes de generar; no sobreescribir versiones; revisor distinto del autor y del área de destino para decidir; decisiones/eventos atómicos; fuentes sujetas a acceso actual. Enumeraciones incluyen estados históricos no usados como nuevas HU. Eventos de revisión son registros inmutables del puerto nuevo, no un broker de dominio.
