from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from threading import RLock
from uuid import UUID

from src.application.ports.output.unidad_trabajo import UnidadTrabajo
from src.domain.entities.informe import Informe
from src.domain.entities.prediccion_contexto import PrediccionContexto
from src.domain.entities.solicitud import Solicitud


@dataclass
class Memoria(UnidadTrabajo):
    solicitudes: dict[UUID, Solicitud] = field(default_factory=dict)
    informes: dict[UUID, Informe] = field(default_factory=dict)
    predicciones: dict[UUID, PrediccionContexto] = field(default_factory=dict)
    lock: RLock = field(default_factory=RLock)

    @contextmanager
    def transaccion(self):
        with self.lock:
            snapshot = deepcopy((self.solicitudes, self.informes, self.predicciones))
            completada = False
            try:
                yield
                completada = True
            finally:
                if not completada:
                    self.solicitudes, self.informes, self.predicciones = snapshot
