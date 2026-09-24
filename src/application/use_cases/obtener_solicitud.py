from src.application.ports.output.solicitud_repository import SolicitudRepository


class ObtenerSolicitud:

    def __init__(self, repository: SolicitudRepository):
        self.repository = repository

    def ejecutar(self, solicitud_id: int):
        return self.repository.obtener_por_id(solicitud_id)