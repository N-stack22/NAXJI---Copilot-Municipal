from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.plantilla import Plantilla


class PlantillaRepository(ABC):
    @abstractmethod
    def listar(self) -> list[Plantilla]: ...

    @abstractmethod
    def obtener_por_id(self, plantilla_id: UUID) -> Plantilla | None: ...
