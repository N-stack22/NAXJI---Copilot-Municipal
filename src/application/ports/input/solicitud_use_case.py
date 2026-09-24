from abc import ABC, abstractmethod
from src.domain.entities.solicitud import Solicitud


class SolicitudUseCase(ABC):

    @abstractmethod
    def ejecutar(self, solicitud: Solicitud) -> Solicitud:
        pass