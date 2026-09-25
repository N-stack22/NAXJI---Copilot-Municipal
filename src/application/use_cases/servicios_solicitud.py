"""Reglas compartidas de aplicación; todas las dependencias son puertos."""
from dataclasses import dataclass
from uuid import UUID

from src.application.ports.output.catalogo_repository import CatalogoRepository
from src.application.ports.output.plantilla_repository import PlantillaRepository
from src.application.ports.output.prediccion_repository import PrediccionRepository
from src.application.ports.output.solicitud_repository import SolicitudRepository
from src.application.ports.output.unidad_trabajo import UnidadTrabajo
from src.domain.entities.solicitud import Solicitud, ahora
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import DatosInvalidos, NoAutorizado, NoEncontrado
from src.domain.services.solicitud_service import SolicitudService
from src.domain.value_objects.estado_solicitud import EstadoSolicitud
from src.domain.value_objects.estados import ResultadoValidacion, Rol


def autorizar(usuario: UsuarioActual, propietario: UUID | None = None,
              escritura: bool = False) -> None:
    if not usuario.activo or not usuario.roles:
        raise NoAutorizado("El perfil no está activo o no tiene roles")
    if escritura and not usuario.roles.intersection({Rol.FUNCIONARIO, Rol.ADMINISTRADOR}):
        raise NoAutorizado("El rol no permite elaborar informes")
    if propietario is not None and usuario.id != propietario and Rol.ADMINISTRADOR not in usuario.roles:
        raise NoAutorizado("No tiene acceso a este recurso")


@dataclass
class ServiciosSolicitud:
    solicitudes: SolicitudRepository
    plantillas: PlantillaRepository
    predicciones: PrediccionRepository
    catalogos: CatalogoRepository
    uow: UnidadTrabajo

    def obtener(self, solicitud_id: UUID, usuario: UsuarioActual,
                escritura: bool = False) -> Solicitud:
        autorizar(usuario, escritura=escritura)
        solicitud = self.solicitudes.obtener_por_id(solicitud_id)
        if solicitud is None:
            raise NoEncontrado("Solicitud no encontrada")
        autorizar(usuario, solicitud.usuario_id, escritura)
        return solicitud

    def plantilla(self, plantilla_id: UUID | None):
        plantilla = self.plantillas.obtener_por_id(plantilla_id) if plantilla_id else None
        if plantilla is None or not plantilla.activa:
            raise NoEncontrado("Plantilla activa no encontrada")
        return plantilla

    def validar_referencias(self, solicitud: Solicitud) -> None:
        SolicitudService.validar(solicitud)
        tipos = {t.id for t in self.catalogos.tipos_informe() if t.activo}
        areas = {a.id for a in self.catalogos.areas() if a.activo}
        if solicitud.tipo_informe_id is not None and solicitud.tipo_informe_id not in tipos:
            raise NoEncontrado("Tipo de informe activo no encontrado")
        for area in (solicitud.area_origen_id, solicitud.area_destino_id):
            if area is not None and area not in areas:
                raise NoEncontrado("Área activa no encontrada")
        if solicitud.plantilla_id:
            plantilla = self.plantilla(solicitud.plantilla_id)
            if solicitud.tipo_informe_id is None:
                solicitud.tipo_informe_id = plantilla.tipo_informe_id
            if plantilla.tipo_informe_id != solicitud.tipo_informe_id:
                raise DatosInvalidos("La plantilla no corresponde al tipo de informe")
            if plantilla.area_id and plantilla.area_id != solicitud.area_destino_id:
                raise DatosInvalidos("La plantilla requiere su área de destino")

    def recalcular_estado(self, solicitud: Solicitud) -> None:
        solicitud.estado = EstadoSolicitud.BORRADOR
        prediccion = self.predicciones.ultima(solicitud.id)
        if (not prediccion or prediccion.resultado_validacion not in (
            ResultadoValidacion.ACEPTADA, ResultadoValidacion.CORREGIDA,
        ) or not solicitud.plantilla_id or not solicitud.tipo_informe_id
                or not solicitud.area_destino_id):
            return
        try:
            SolicitudService.validar_obligatorios(solicitud, self.plantilla(solicitud.plantilla_id))
        except DatosInvalidos:
            return  # Se permite guardar formularios incompletos como BORRADOR.
        solicitud.estado = EstadoSolicitud.LISTA_PARA_GENERAR

    def guardar(self, solicitud: Solicitud) -> Solicitud:
        solicitud.updated_at = ahora()
        return self.solicitudes.guardar(solicitud)
