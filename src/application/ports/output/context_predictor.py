from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.prediccion_contexto import PrediccionContexto


class ContextPredictor(ABC):
    @abstractmethod
    def predecir(self, asunto: str, solicitud_id: UUID) -> PrediccionContexto: ...
