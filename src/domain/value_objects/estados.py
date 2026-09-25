from enum import Enum


class EstadoInforme(str, Enum):
    BORRADOR = "BORRADOR"
    EN_REVISION = "EN_REVISION"
    OBSERVADO = "OBSERVADO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ARCHIVADO = "ARCHIVADO"


class ResultadoValidacion(str, Enum):
    PENDIENTE = "PENDIENTE"
    ACEPTADA = "ACEPTADA"
    CORREGIDA = "CORREGIDA"
    RECHAZADA = "RECHAZADA"


class OrigenVersion(str, Enum):
    IA = "IA"
    USUARIO = "USUARIO"
    REVISION = "REVISION"
    SISTEMA = "SISTEMA"


class TipoDato(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    DATE = "date"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class Rol(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    FUNCIONARIO = "FUNCIONARIO"
    REVISOR = "REVISOR"
    APROBADOR = "APROBADOR"
