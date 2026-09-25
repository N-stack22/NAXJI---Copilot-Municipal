from enum import Enum


class EstadoSolicitud(str, Enum):
    BORRADOR = "BORRADOR"
    LISTA_PARA_GENERAR = "LISTA_PARA_GENERAR"
    PROCESANDO = "PROCESANDO"
    GENERADA = "GENERADA"
    CANCELADA = "CANCELADA"
