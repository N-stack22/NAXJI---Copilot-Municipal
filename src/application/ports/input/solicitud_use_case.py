from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID
from src.domain.entities.solicitud import Solicitud
from src.domain.entities.usuario_actual import UsuarioActual


@dataclass(frozen=True)
class DatosSolicitud:
    asunto: str
    tipo_informe_id: UUID | None = None
    plantilla_id: UUID | None = None
    area_origen_id: UUID | None = None
    area_destino_id: UUID | None = None


class SolicitudUseCase(ABC):

    @abstractmethod
    def ejecutar(self, usuario: UsuarioActual, datos: DatosSolicitud) -> Solicitud:
        pass
