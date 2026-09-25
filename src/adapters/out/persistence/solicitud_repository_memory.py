from typing import Optional
from copy import deepcopy
from uuid import UUID

from src.domain.entities.solicitud import Solicitud
from src.application.ports.output.solicitud_repository import SolicitudRepository
from src.adapters.out.persistence.memoria import Memoria


class SolicitudRepositoryMemory(SolicitudRepository):

    def __init__(self, memoria: Memoria | None = None):
        self.memoria = memoria if memoria is not None else Memoria()

    def guardar(self, solicitud: Solicitud) -> Solicitud:
        with self.memoria.lock:
            self.memoria.solicitudes[solicitud.id] = deepcopy(solicitud)
            return deepcopy(solicitud)

    def obtener_por_id(self, solicitud_id: UUID) -> Optional[Solicitud]:
        with self.memoria.lock:
            return deepcopy(self.memoria.solicitudes.get(solicitud_id))
