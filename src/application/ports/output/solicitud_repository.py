from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.solicitud import Solicitud


class SolicitudRepository(ABC):

    @abstractmethod
    def guardar(self, solicitud: Solicitud) -> Solicitud:
        pass

    @abstractmethod
    def obtener_por_id(self, solicitud_id: int) -> Optional[Solicitud]:
        pass