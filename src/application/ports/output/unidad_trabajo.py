from abc import ABC, abstractmethod
from contextlib import AbstractContextManager


class UnidadTrabajo(ABC):
    @abstractmethod
    def transaccion(self) -> AbstractContextManager[None]:
        """Commit conjunto o rollback de solicitudes, predicciones e informes.

        Serializa modificaciones concurrentes del mismo agregado. El adaptador
        real debe proporcionar garantías equivalentes (transacción/bloqueo).
        """
        ...
