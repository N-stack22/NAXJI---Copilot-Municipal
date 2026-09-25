from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.informe import Informe


class InformeRepository(ABC):
    @abstractmethod
    def guardar(self, informe: Informe) -> Informe:
        """Persiste informes + versiones_informe; solicitud_id y números de versión únicos."""
        ...

    @abstractmethod
    def obtener_por_id(self, informe_id: UUID) -> Informe | None: ...

    @abstractmethod
    def obtener_por_solicitud(self, solicitud_id: UUID) -> Informe | None: ...
