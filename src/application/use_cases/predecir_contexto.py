from math import isfinite
from uuid import UUID

from src.application.ports.output.context_predictor import ContextPredictor
from src.application.use_cases.servicios_solicitud import ServiciosSolicitud
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import DatosInvalidos
from src.domain.services.solicitud_service import SolicitudService
from src.domain.value_objects.estado_solicitud import EstadoSolicitud
from src.domain.value_objects.estados import ResultadoValidacion


class PredecirContexto:
    def __init__(self, servicios: ServiciosSolicitud, predictor: ContextPredictor):
        self.s, self.predictor = servicios, predictor

    def ejecutar(self, solicitud_id: UUID, usuario: UsuarioActual):
        with self.s.uow.transaccion():
            solicitud = self.s.obtener(solicitud_id, usuario, escritura=True)
            SolicitudService.editable(solicitud)
            prediccion = self.predictor.predecir(solicitud.asunto, solicitud.id)
            if prediccion.solicitud_id != solicitud.id or not prediccion.modelo.strip():
                raise DatosInvalidos("Respuesta del predictor incompatible con la solicitud")
            confianzas = [prediccion.confianza_tipo, prediccion.confianza_area,
                          *(n.confianza for n in prediccion.normativas)]
            if any(c is not None and (not isfinite(c) or not 0 <= c <= 1) for c in confianzas):
                raise DatosInvalidos("La confianza del predictor debe estar entre 0 y 1")
            tipos = {t.id for t in self.s.catalogos.tipos_informe() if t.activo}
            areas = {a.id for a in self.s.catalogos.areas() if a.activo}
            if prediccion.tipo_informe_predicho_id not in tipos or prediccion.area_destino_predicha_id not in areas:
                raise DatosInvalidos("El predictor devolvió referencias de catálogo desconocidas")
            ids = [n.normativa_id for n in prediccion.normativas]
            if len(set(ids)) != len(ids):
                raise DatosInvalidos("El predictor devolvió normativas duplicadas")
            for n in prediccion.normativas:
                norma = self.s.catalogos.normativa(n.normativa_id)
                if not norma or not norma.activo or (n.orden is not None and n.orden < 1):
                    raise DatosInvalidos("Normativa predicha inválida")
                n.aceptada = None
            prediccion.parametros["asunto"] = solicitud.asunto
            prediccion.resultado_validacion = ResultadoValidacion.PENDIENTE
            prediccion.validado_por = prediccion.validado_at = None
            solicitud.estado = EstadoSolicitud.BORRADOR
            self.s.guardar(solicitud)
            return self.s.predicciones.guardar(prediccion)
