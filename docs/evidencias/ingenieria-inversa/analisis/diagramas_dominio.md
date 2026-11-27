# UML textual — dominio de NAXJI

Reconstrucción manual desde código de `main` **4f4d294**, corte **27/11/2026**. Los diagramas son documentación Mermaid, no resultados generados por Understand ni nuevos diseños para implementar. [Dominio completo y reglas](dominio.md), [inventario de símbolos](../cierre-documental-20261127/inventario-fuente.json).

Las clases y operaciones mostradas existen en el repositorio. Se seleccionan campos para legibilidad; la nulabilidad y los tipos completos están en el inventario y código. Las cardinalidades reflejan listas/referencias/contratos de aplicación, no una verificación de todas las FK en una base desplegada. Las composiciones describen agregados observados, sin una clase `AggregateRoot` propia.

| Diagrama | Código que respalda su lectura |
| ---| ---|
| Clases | [Entidades](../../../../src/domain/entities/), [SeccionSalida](../../../../src/domain/value_objects/seccion_salida.py), [contratos de repositorios](../../../../src/application/ports/output/) |
| Solicitud | [ServiciosSolicitud](../../../../src/application/use_cases/servicios_solicitud.py), [ActualizarSolicitud](../../../../src/application/use_cases/actualizar_solicitud.py), [GenerarBorrador](../../../../src/application/use_cases/generar_borrador.py) |
| Informe | [ActualizarBorrador](../../../../src/application/use_cases/actualizar_borrador.py), [RevisionInformes](../../../../src/application/use_cases/revision_informes.py) |
| Documento | [GestionDocumentos](../../../../src/application/use_cases/documentos.py), [DocumentosPostgres](../../../../src/adapters/out/persistence/documentos_postgres.py) |
| Secuencia de decisión | [RevisionInformes.decidir](../../../../src/application/use_cases/revision_informes.py), [InformeAuditado](../../../../src/adapters/out/persistence/informe_auditado.py), [PostgresUnidadTrabajo/InformeRepositoryPostgres](../../../../src/adapters/out/persistence/postgres.py), [RevisionPostgres](../../../../src/adapters/out/persistence/revision_postgres.py) |

## Clases y relaciones

[Fuente Mermaid](diagramas/clases-dominio.mmd).

```mermaid
classDiagram
  class Solicitud {
    UUID id
    UUID usuario_id
    str asunto
    EstadoSolicitud estado
  }
  class SolicitudValor {
    UUID id
    UUID campo_plantilla_id
    Any valor
  }
  class Plantilla {
    UUID id
    UUID tipo_informe_id
    int version
    bool activa
  }
  class CampoPlantilla {
    UUID id
    str clave
    TipoDato tipo_dato
    bool obligatorio
  }
  class SeccionSalida {
    str clave
    str titulo
    bool obligatoria
  }
  class Informe {
    UUID id
    UUID solicitud_id
    EstadoInforme estado
  }
  class VersionInforme {
    UUID id
    int numero_version
    dict contenido
    OrigenVersion origen
    dict sustento
  }
  class PrediccionContexto {
    UUID id
    UUID solicitud_id
    ResultadoValidacion resultado_validacion
  }
  class NormativaPredicha {
    UUID id
    UUID normativa_id
    bool aceptada
  }
  class Documento {
    UUID id
    UUID usuario_id
    str ambito
    str estado
    str sha256
    int fragmentos
  }
  class UsuarioActual {
    UUID id
    UUID area_id
    bool activo
  }
  class TipoInforme {
    UUID id
    str codigo
  }
  class AreaMunicipal {
    UUID id
    UUID area_padre_id
  }
  class Normativa {
    UUID id
    str titulo
  }
  class CorrespondenciaNormativa {
    str etiqueta
    elegible()
    evidencia()
  }
  Solicitud "1" *-- "0..*" SolicitudValor : valores
  Plantilla "1" *-- "0..*" CampoPlantilla : campos
  Plantilla "1" o-- "0..*" SeccionSalida : estructura opcional
  Informe "1" *-- "0..*" VersionInforme : versiones
  VersionInforme "1" o-- "0..*" SeccionSalida : snapshot opcional
  PrediccionContexto "1" *-- "0..*" NormativaPredicha : propuestas
  Solicitud "1" --> "0..*" PrediccionContexto : solicitud_id
  Solicitud "1" --> "0..1" Informe : solicitud_id y contrato de generacion
  Solicitud --> Plantilla : plantilla_id opcional
  Solicitud --> TipoInforme : tipo_informe_id opcional
  Solicitud --> AreaMunicipal : origen y destino por UUID
  SolicitudValor --> CampoPlantilla : campo_plantilla_id
  Plantilla --> TipoInforme : tipo_informe_id
  Plantilla --> AreaMunicipal : area_id opcional
  Informe --> Plantilla : plantilla_id
  Solicitud --> UsuarioActual : usuario_id de identidad
  Documento --> UsuarioActual : usuario_id de identidad
  NormativaPredicha --> Normativa : normativa_id
  CorrespondenciaNormativa --> Normativa : normativa
  note for Solicitud "Relaciones por campos del codigo; no representa un esquema SQL completo"
  note for Informe "La lista inicia vacia; generar publica la primera version"
  note for Documento "Fragmentos son filas/diccionarios; no hay clase Fragmento"
  note for SeccionSalida "Objeto de valor congelado; None aplica estructura legacy"
```

## Estados de solicitud

[Fuente Mermaid](diagramas/estados-solicitud.mmd).

```mermaid
stateDiagram-v2
  [*] --> BORRADOR : CrearSolicitud
  BORRADOR --> LISTA_PARA_GENERAR : contexto confirmado y obligatorios completos
  LISTA_PARA_GENERAR --> BORRADOR : cambio invalida contexto o datos
  BORRADOR --> CANCELADA : ActualizarSolicitud
  LISTA_PARA_GENERAR --> CANCELADA : ActualizarSolicitud
  LISTA_PARA_GENERAR --> PROCESANDO : GenerarBorrador._reservar
  PROCESANDO --> GENERADA : publicacion atomica o informe ya existente
  PROCESANDO --> LISTA_PARA_GENERAR : fallo o reserva vencida con datos validos
  PROCESANDO --> BORRADOR : fallo o reserva vencida con datos incompletos
  note right of PROCESANDO
    Inferencia fuera de transaccion
    Publicar requiere intento vigente
  end note
  note right of GENERADA
    No hay reapertura implementada
  end note
```

## Estados de informe

[Fuente Mermaid](diagramas/estados-informe.mmd).

```mermaid
stateDiagram-v2
  [*] --> BORRADOR : GenerarBorrador crea version IA
  BORRADOR --> BORRADOR : ActualizarBorrador agrega version USUARIO
  BORRADOR --> EN_REVISION : RevisionInformes.enviar
  EN_REVISION --> EN_REVISION : editar agrega version REVISION
  EN_REVISION --> APROBADO : decidir con comprobaciones humanas y fuentes accesibles
  EN_REVISION --> RECHAZADO : decidir con motivo
  APROBADO --> APROBADO : exportar version aprobada y registrar evento
  note right of EN_REVISION
    Revisor del area de destino
    Distinto del creador y propietario
    Control de version vigente
  end note
  note right of RECHAZADO
    No hay reapertura implementada
    OBSERVADO y ARCHIVADO solo constan en el enum
  end note
```

## Estados de documento

[Fuente Mermaid](diagramas/estados-documento.mmd).

```mermaid
stateDiagram-v2
  [*] --> SUBIENDO : cargar archivo autorizado
  SUBIENDO --> CARGADO : almacen confirma y finaliza intento
  SUBIENDO --> ERROR_CARGA : ErrorServicio del almacen
  ERROR_CARGA --> SUBIENDO : reenviar mismo archivo
  SUBIENDO --> SUBIENDO : reintento tras vencer reserva
  CARGADO --> PROCESANDO : procesar
  ERROR_PROCESAMIENTO --> PROCESANDO : reintentar
  PROCESANDO --> INDEXADO : finalizar con fragmentos en transaccion
  PROCESANDO --> ERROR_PROCESAMIENTO : fallo de extraccion o embeddings
  INDEXADO --> INDEXADO : misma revision de procesamiento
  INDEXADO --> PROCESANDO : otra revision de procesamiento
  PROCESANDO --> PROCESANDO : nuevo intento tras vencer reserva
  note right of INDEXADO
    No hay clase EstadoDocumento
    Estado es una cadena
  end note
```

## Secuencia de decision PMV 3

[Fuente Mermaid](diagramas/secuencia-revision.mmd).

```mermaid
sequenceDiagram
  actor Persona as Revisor del area de destino
  participant API as revision_controller
  participant Caso as RevisionInformes
  participant UoW as PostgresUnidadTrabajo
  participant Informes as InformeAuditado
  participant Repo as InformeRepositoryPostgres
  participant Eventos as RevisionPostgres
  Persona->>API: decidir numero_version, decision, motivo, comprobaciones
  API->>Caso: decidir(...)
  Caso->>UoW: transaccion()
  Caso->>Informes: obtener_por_id(informe_id)
  Informes->>Repo: obtener_por_id(informe_id)
  Repo-->>Caso: informe con bloqueo de fila en UoW activa
  Note over Caso: autor distinto, area de destino, version vigente y EN_REVISION
  Note over Caso: APROBADO exige comprobaciones y fuentes accesibles
  Caso->>Informes: guardar(informe con decision)
  Informes->>Repo: guardar(informe)
  Note over Informes: no hay nueva version en una decision; no duplica CREAR_VERSION
  Caso->>Eventos: registrar(evento de decision)
  alt todas las operaciones validas
    UoW-->>Caso: commit conjunto
    Caso-->>API: historial autorizado y fuentes protegidas
    API-->>Persona: resultado
  else conflicto o fallo dentro de transaccion
    UoW-->>Caso: rollback conjunto
    Caso-->>API: error de dominio o persistencia sanitizado
  end
```
