from copy import deepcopy
from uuid import UUID

from src.adapters.out.persistence.memoria import Memoria
from src.application.ports.output.prediccion_repository import PrediccionRepository
from src.domain.entities.prediccion_contexto import PrediccionContexto


class PrediccionRepositoryMemory(PrediccionRepository):
    def __init__(self, memoria: Memoria):
        self.memoria = memoria

    def guardar(self, prediccion: PrediccionContexto) -> PrediccionContexto:
        with self.memoria.lock:
            self.memoria.predicciones[prediccion.id] = deepcopy(prediccion)
            return deepcopy(prediccion)

    def ultima(self, solicitud_id: UUID) -> PrediccionContexto | None:
        with self.memoria.lock:
            candidatas = [p for p in self.memoria.predicciones.values()
                          if p.solicitud_id == solicitud_id]
            return deepcopy(max(candidatas, key=lambda p: p.created_at, default=None))
