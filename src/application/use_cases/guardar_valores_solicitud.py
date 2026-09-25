from uuid import UUID

from src.application.use_cases.servicios_solicitud import ServiciosSolicitud
from src.domain.entities.solicitud import SolicitudValor, ahora
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import DatosInvalidos
from src.domain.services.solicitud_service import SolicitudService


class GuardarValoresSolicitud:
    def __init__(self, servicios: ServiciosSolicitud):
        self.s = servicios

    def ejecutar(self, solicitud_id: UUID, usuario: UsuarioActual, valores: dict):
        """Reemplaza el conjunto de valores, conservando IDs de los campos existentes."""
        with self.s.uow.transaccion():
            solicitud = self.s.obtener(solicitud_id, usuario, escritura=True)
            SolicitudService.editable(solicitud)
            plantilla = self.s.plantilla(solicitud.plantilla_id)
            campos = {c.id: c for c in plantilla.campos if c.activo}
            if valores.keys() - campos.keys():
                raise DatosInvalidos("Un campo no pertenece a la plantilla activa")
            anteriores = {v.campo_plantilla_id: v for v in solicitud.valores}
            nuevos = []
            for campo_id, valor in valores.items():
                SolicitudService.validar_valor(campos[campo_id], valor)
                item = anteriores.get(campo_id) or SolicitudValor(solicitud.id, campo_id, valor)
                item.valor, item.updated_at = valor, ahora()
                nuevos.append(item)
            solicitud.valores = nuevos
            self.s.recalcular_estado(solicitud)
            return self.s.guardar(solicitud)
