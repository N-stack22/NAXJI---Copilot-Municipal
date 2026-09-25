from uuid import UUID
from src.application.use_cases.servicios_solicitud import ServiciosSolicitud
from src.domain.entities.usuario_actual import UsuarioActual


class ObtenerSolicitud:

    def __init__(self, servicios: ServiciosSolicitud):
        self.servicios = servicios

    def ejecutar(self, solicitud_id: UUID, usuario: UsuarioActual):
        return self.servicios.obtener(solicitud_id, usuario)
