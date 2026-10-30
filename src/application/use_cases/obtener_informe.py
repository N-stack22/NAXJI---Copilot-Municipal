from uuid import UUID
from copy import deepcopy

from src.application.ports.output.informe_repository import InformeRepository
from src.application.use_cases.servicios_solicitud import ServiciosSolicitud
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import NoEncontrado


class ObtenerInforme:
    def __init__(self, servicios: ServiciosSolicitud, informes: InformeRepository, documentos=None, *, proteger_fuentes=True):
        self.s, self.informes = servicios, informes
        self.documentos = documentos
        self.proteger_fuentes = proteger_fuentes

    def proteger(self, informe, usuario):
        if not self.proteger_fuentes:
            return informe
        if self.documentos:
            return self.documentos.proteger(informe, usuario)
        informe = deepcopy(informe)
        for version in informe.versiones:
            if version.sustento:
                version.sustento["fuentes"] = [{"sin_acceso": True, "citas": []}
                                                for _ in version.sustento["fuentes"]]
        return informe

    def ejecutar(self, informe_id: UUID, usuario: UsuarioActual):
        informe = self.informes.obtener_por_id(informe_id)
        if informe is None:
            raise NoEncontrado("Informe no encontrado")
        self.s.obtener(informe.solicitud_id, usuario)
        return self.proteger(informe, usuario)

    def por_solicitud(self, solicitud_id: UUID, usuario: UsuarioActual):
        self.s.obtener(solicitud_id, usuario)
        informe = self.informes.obtener_por_solicitud(solicitud_id)
        if informe is None:
            raise NoEncontrado("Informe no encontrado")
        return self.proteger(informe, usuario)
