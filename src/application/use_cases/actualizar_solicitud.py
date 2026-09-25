from uuid import UUID

from src.application.use_cases.servicios_solicitud import ServiciosSolicitud
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import ConflictoEstado, DatosInvalidos
from src.domain.services.solicitud_service import SolicitudService
from src.domain.value_objects.estado_solicitud import EstadoSolicitud
from src.domain.value_objects.estados import ResultadoValidacion


class ActualizarSolicitud:
    def __init__(self, servicios: ServiciosSolicitud):
        self.s = servicios

    def ejecutar(self, solicitud_id: UUID, usuario: UsuarioActual, cambios: dict):
        permitidos = {"asunto", "tipo_informe_id", "plantilla_id", "area_origen_id", "area_destino_id", "estado"}
        if not cambios or cambios.keys() - permitidos:
            raise DatosInvalidos("Debe indicar campos editables de la solicitud")
        with self.s.uow.transaccion():
            solicitud = self.s.obtener(solicitud_id, usuario, escritura=True)
            SolicitudService.editable(solicitud)
            estado = cambios.get("estado")
            if "estado" in cambios and estado != EstadoSolicitud.CANCELADA:
                raise ConflictoEstado("Solo se permite cancelar manualmente; los demás estados son automáticos")
            invalida = any(k in cambios and cambios[k] != getattr(solicitud, k)
                           for k in ("asunto", "tipo_informe_id", "area_destino_id"))
            if "plantilla_id" in cambios and cambios["plantilla_id"] != solicitud.plantilla_id:
                solicitud.valores = []
            for clave, valor in cambios.items():
                if clave != "estado":
                    setattr(solicitud, clave, valor)
            self.s.validar_referencias(solicitud)
            solicitud.asunto = solicitud.asunto.strip()
            prediccion = self.s.predicciones.ultima(solicitud.id)
            if invalida and prediccion:
                prediccion.resultado_validacion = ResultadoValidacion.PENDIENTE
                prediccion.validado_por = prediccion.validado_at = None
                for normativa in prediccion.normativas:
                    normativa.aceptada = None
                self.s.predicciones.guardar(prediccion)
            self.s.recalcular_estado(solicitud)
            if estado == EstadoSolicitud.CANCELADA:
                solicitud.estado = EstadoSolicitud.CANCELADA
            return self.s.guardar(solicitud)
