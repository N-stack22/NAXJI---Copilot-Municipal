from dataclasses import asdict
from src.application.ports.input.solicitud_use_case import DatosSolicitud, SolicitudUseCase
from src.application.use_cases.servicios_solicitud import ServiciosSolicitud, autorizar
from src.domain.entities.solicitud import Solicitud
from src.domain.entities.usuario_actual import UsuarioActual


class CrearSolicitud(SolicitudUseCase):

    def __init__(self, servicios: ServiciosSolicitud):
        self.servicios = servicios

    def ejecutar(self, usuario: UsuarioActual, datos: DatosSolicitud) -> Solicitud:
        autorizar(usuario, escritura=True)
        solicitud = Solicitud(usuario_id=usuario.id, **asdict(datos))
        if solicitud.area_origen_id is None:
            solicitud.area_origen_id = usuario.area_id
        self.servicios.validar_referencias(solicitud)
        solicitud.asunto = solicitud.asunto.strip()
        with self.servicios.uow.transaccion():
            return self.servicios.solicitudes.guardar(solicitud)
