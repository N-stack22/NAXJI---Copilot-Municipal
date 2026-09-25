from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.prediccion_contexto import PrediccionContexto


class PrediccionRepository(ABC):
    @abstractmethod
    def guardar(self, prediccion: PrediccionContexto) -> PrediccionContexto:
        """Persiste predicciones_ia + prediccion_normativas (prediccion_id del agregado)."""
        ...

    @abstractmethod
    def ultima(self, solicitud_id: UUID) -> PrediccionContexto | None: ...
