from src.domain.entities.solicitud import Solicitud
from src.domain.services.solicitud_service import SolicitudService
from src.application.ports.output.solicitud_repository import SolicitudRepository


class CrearSolicitud:

    def __init__(self, repository: SolicitudRepository):
        self.repository = repository

    def ejecutar(self, solicitud: Solicitud) -> Solicitud:
        SolicitudService.validar(solicitud)
        return self.repository.guardar(solicitud)