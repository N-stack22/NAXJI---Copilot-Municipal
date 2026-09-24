from enum import Enum


class EstadoSolicitud(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADA = "COMPLETADA"