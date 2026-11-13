"""Adaptadores del esquema PMV1 existente. No ejecutan migraciones ni datos semilla."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import fields
from datetime import date
from enum import Enum
from uuid import UUID

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from src.adapters.out.persistence.sql_resources import consulta
from src.application.ports.output.unidad_trabajo import UnidadTrabajo
from src.application.ports.output.catalogo_repository import CatalogoRepository
from src.application.ports.output.plantilla_repository import PlantillaRepository
from src.application.ports.output.solicitud_repository import SolicitudRepository
from src.application.ports.output.prediccion_repository import PrediccionRepository
from src.application.ports.output.informe_repository import InformeRepository
from src.domain.entities.catalogo import TipoInforme, AreaMunicipal, Normativa
from src.domain.entities.correspondencia_normativa import CorrespondenciaNormativa
from src.domain.entities.plantilla import Plantilla, CampoPlantilla
from src.domain.entities.solicitud import Solicitud, SolicitudValor
from src.domain.entities.prediccion_contexto import PrediccionContexto, NormativaPredicha
from src.domain.entities.informe import Informe, VersionInforme
from src.domain.services.errores import ConflictoEstado, DatosInvalidos
from src.domain.value_objects.estado_solicitud import EstadoSolicitud
from src.domain.value_objects.estados import EstadoInforme, OrigenVersion, ResultadoValidacion, TipoDato
from src.domain.value_objects.seccion_salida import secciones_desde_json, secciones_a_json
from src.infrastructure.configuration.database import DatabaseSettings, database_error


class PersistenceError(RuntimeError):
    """Error sanitizado: nunca incluye SQL, parámetros ni mensajes del proveedor."""


class PostgresUnidadTrabajo(UnidadTrabajo):
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self._current = ContextVar("naxji_connection", default=None)

    @property
    def active(self):
        return self._current.get() is not None

    @contextmanager
    def transaccion(self):
        if self.active:
            # Savepoint: también revierte errores capturados por el llamador.
            with self._current.get().transaction():
                yield
            return
        try:
            with self.settings.connect(row_factory=dict_row) as connection:
                token = self._current.set(connection)
                try:
                    yield
                finally:
                    self._current.reset(token)
        except psycopg.errors.UniqueViolation:
            raise ConflictoEstado("El registro o número de versión ya existe") from None
        except (psycopg.errors.ForeignKeyViolation, psycopg.errors.CheckViolation):
            raise DatosInvalidos("Referencias o valores incompatibles con el esquema PostgreSQL") from None
        except psycopg.Error as error:
            raise PersistenceError(database_error(error)) from None

    @contextmanager
    def connection(self, *, write=False):
        if self.active:
            yield self._current.get()
        elif write:
            with self.transaccion():
                yield self._current.get()
        else:
            try:
                with self.settings.connect(row_factory=dict_row) as connection:
                    connection.execute(consulta("postgres", "lectura_consistente"))
                    yield connection
            except psycopg.Error as error:
                raise PersistenceError(database_error(error)) from None


def entity(cls, row, **enums):
    values = {f.name: row[f.name] for f in fields(cls) if f.name in row}
    if "secciones_salida" in values:
        values["secciones_salida"] = secciones_desde_json(values["secciones_salida"])
    for name, enum in enums.items():
        values[name] = enum(values[name])
    for name in ("confianza", "confianza_tipo", "confianza_area"):
        if values.get(name) is not None:
            values[name] = float(values[name])
    return cls(**values)


def save(connection, table, item, *, omit=(), json_fields=(), extra=None, insert_only=False):
    """Los identificadores provienen solo de clases internas, nunca del cliente HTTP."""
    values = {f.name: getattr(item, f.name) for f in fields(item) if f.name not in omit
              and not (f.name == "sustento" and getattr(item, f.name) is None)}
    values.update(extra or {})
    for key, value in values.items():
        if key == "secciones_salida":
            # SQL NULL conserva el contrato anterior; JSON null no es una estructura.
            values[key] = None if value is None else Jsonb(secciones_a_json(value))
        elif key in json_fields:
            values[key] = Jsonb(value)
        elif isinstance(value, Enum):
            values[key] = value.value
    columns = list(values)
    statement = sql.SQL(consulta("postgres", "save_insert")).format(
        sql.Identifier(table), sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
    )
    if not insert_only:
        updates = [c for c in columns if c not in {"id", "created_at"}]
        statement += sql.SQL(" " + consulta("postgres", "save_upsert") + " ") + sql.SQL(", ").join(
            sql.SQL(consulta("postgres", "save_assignment")).format(sql.Identifier(c), sql.Identifier(c)) for c in updates
        )
    connection.execute(statement, list(values.values()))


class Repository:
    def __init__(self, uow):
        self.uow = uow

    def lock(self):
        return " " + consulta("postgres", "bloquear") if self.uow.active else ""


class CatalogoRepositoryPostgres(Repository, CatalogoRepository):
    def correspondencias_normativas(self, etiquetas):
        if not etiquetas:
            return []
        with self.uow.connection() as c:
            # Despliegue aditivo: hasta aplicar la migración solo se muestran temas.
            if c.execute(consulta("postgres", "existe_correspondencias")).fetchone()["tabla"] is None:
                return []
            rows = c.execute(consulta("postgres", "correspondencias"), (etiquetas,)).fetchall()
            resultado = []
            for row in rows:
                documento = row.pop("documento")
                documento["id"] = UUID(documento["id"])
                # JSONB serializa fechas; las entidades conservan su tipo date.
                for key in ("fecha_publicacion", "fecha_inicio_vigencia", "fecha_fin_vigencia"):
                    if documento.get(key):
                        documento[key] = date.fromisoformat(documento[key])
                resultado.append(entity(CorrespondenciaNormativa, {**row, "normativa": entity(Normativa, documento)}))
            return resultado

    def tipos_informe(self):
        with self.uow.connection() as c:
            return [entity(TipoInforme, r) for r in c.execute(consulta("postgres", "tipos_informe"))]

    def areas(self):
        with self.uow.connection() as c:
            return [entity(AreaMunicipal, r) for r in c.execute(consulta("postgres", "areas"))]

    def normativa(self, normativa_id):
        with self.uow.connection() as c:
            row = c.execute(consulta("postgres", "normativa"), (normativa_id,)).fetchone()
            return entity(Normativa, row) if row else None

    def normativa_por_codigo(self, codigo):
        with self.uow.connection() as c:
            row = c.execute(consulta("postgres", "normativa_por_codigo"), (codigo,)).fetchone()
            return entity(Normativa, row) if row else None


class PlantillaRepositoryPostgres(Repository, PlantillaRepository):
    @staticmethod
    def load(c, row):
        item = entity(Plantilla, row)
        item.campos = [entity(CampoPlantilla, r, tipo_dato=TipoDato) for r in c.execute(
            consulta("postgres", "campos_plantilla"), (item.id,))]
        return item

    def listar(self):
        with self.uow.connection() as c:
            rows = c.execute(consulta("postgres", "plantillas")).fetchall()
            return [self.load(c, row) for row in rows]

    def obtener_por_id(self, plantilla_id):
        with self.uow.connection() as c:
            row = c.execute(consulta("postgres", "plantilla"), (plantilla_id,)).fetchone()
            return self.load(c, row) if row else None


class SolicitudRepositoryPostgres(Repository, SolicitudRepository):
    def guardar(self, solicitud):
        with self.uow.connection(write=True) as c:
            save(c, "solicitudes", solicitud, omit=("valores",))
            c.execute(consulta("postgres", "eliminar_valores_ausentes"),
                      (solicitud.id, [v.id for v in solicitud.valores]))
            for value in solicitud.valores:
                save(c, "solicitud_valores", value, json_fields=("valor",))
            # Los triggers PostgreSQL son la autoridad de updated_at.
            # Leer en la misma transacción evita devolver timestamps solo locales.
            return self.obtener_por_id(solicitud.id)

    def obtener_por_id(self, solicitud_id):
        with self.uow.connection() as c:
            row = c.execute(consulta("postgres", "solicitud") + self.lock(), (solicitud_id,)).fetchone()
            if row is None:
                return None
            item = entity(Solicitud, row, estado=EstadoSolicitud)
            item.valores = [entity(SolicitudValor, r) for r in c.execute(
                consulta("postgres", "valores_solicitud"), (item.id,))]
            return item


class PrediccionRepositoryPostgres(Repository, PrediccionRepository):
    def guardar(self, prediccion):
        with self.uow.connection(write=True) as c:
            save(c, "predicciones_ia", prediccion, omit=("normativas",), json_fields=("parametros",))
            c.execute(consulta("postgres", "eliminar_normativas_ausentes"),
                      (prediccion.id, [n.id for n in prediccion.normativas]))
            for norma in prediccion.normativas:
                save(c, "prediccion_normativas", norma, extra={"prediccion_id": prediccion.id})
        return prediccion

    def ultima(self, solicitud_id):
        with self.uow.connection() as c:
            row = c.execute(consulta("postgres", "ultima_prediccion") + self.lock(), (solicitud_id,)).fetchone()
            if row is None:
                return None
            item = entity(PrediccionContexto, row, resultado_validacion=ResultadoValidacion)
            item.normativas = [entity(NormativaPredicha, r) for r in c.execute(
                consulta("postgres", "normativas_prediccion"), (item.id,))]
            return item


class InformeRepositoryPostgres(Repository, InformeRepository):
    def guardar(self, informe):
        numbers = [v.numero_version for v in informe.versiones]
        if len(numbers) != len(set(numbers)) or any(n < 1 for n in numbers):
            raise ConflictoEstado("Número de versión inválido o duplicado")
        with self.uow.connection(write=True) as c:
            save(c, "informes", informe, omit=("versiones",))
            existing = {r["id"] for r in c.execute(consulta("postgres", "versiones_existentes"), (informe.id,))}
            for version in informe.versiones:
                if version.id not in existing:
                    save(c, "versiones_informe", version,
                         omit=("sustento",) if version.sustento is None else (),
                         json_fields=("contenido", "sustento"), insert_only=True)
                    if version.sustento:
                        for fuente in version.sustento["fuentes"]:
                            for cita in fuente["citas"]:
                                c.execute(consulta("postgres", "insertar_cita"),
                                    (version.id, UUID(fuente["documento_id"]), UUID(fuente["fragmento_id"]),
                                     cita["seccion"], cita["pasaje"], cita["estado"], Jsonb(fuente)))
            # El trigger fija updated_at; responder con lo efectivamente guardado.
            return self.load(c, c.execute(consulta("postgres", "informe"), (informe.id,)).fetchone())

    @staticmethod
    def load(c, row):
        if row is None:
            return None
        item = entity(Informe, row, estado=EstadoInforme)
        item.versiones = [entity(VersionInforme, r, origen=OrigenVersion) for r in c.execute(
            consulta("postgres", "versiones_informe"), (item.id,))]
        return item

    def obtener_por_id(self, informe_id):
        with self.uow.connection() as c:
            return self.load(c, c.execute(consulta("postgres", "informe") + self.lock(), (informe_id,)).fetchone())

    def obtener_por_solicitud(self, solicitud_id):
        with self.uow.connection() as c:
            return self.load(c, c.execute(consulta("postgres", "informe_por_solicitud") + self.lock(), (solicitud_id,)).fetchone())
