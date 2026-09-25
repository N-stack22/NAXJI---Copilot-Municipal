from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.solicitud import Solicitud


class SolicitudRepository(ABC):

    @abstractmethod
    def guardar(self, solicitud: Solicitud) -> Solicitud:
        """Inserta/actualiza el agregado solicitudes + solicitud_valores conservando IDs."""
        pass

    @abstractmethod
    def obtener_por_id(self, solicitud_id: UUID) -> Optional[Solicitud]:
        pass
