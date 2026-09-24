from typing import Optional

from src.domain.entities.solicitud import Solicitud
from src.application.ports.output.solicitud_repository import SolicitudRepository


class SolicitudRepositoryMemory(SolicitudRepository):

    def __init__(self):
        self.solicitudes = {}
        self.secuencia = 1

    def guardar(self, solicitud: Solicitud) -> Solicitud:
        solicitud.id = self.secuencia
        self.solicitudes[self.secuencia] = solicitud
        self.secuencia += 1

        return solicitud

    def obtener_por_id(self, solicitud_id: int) -> Optional[Solicitud]:
        return self.solicitudes.get(solicitud_id)