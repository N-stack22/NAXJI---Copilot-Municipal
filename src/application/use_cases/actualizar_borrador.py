from uuid import UUID

from src.application.ports.output.informe_repository import InformeRepository
from src.application.use_cases.obtener_informe import ObtenerInforme
from src.application.use_cases.servicios_solicitud import ServiciosSolicitud, autorizar
from src.domain.entities.informe import VersionInforme
from src.domain.entities.solicitud import ahora
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import ConflictoEstado, DatosInvalidos
from src.domain.services.informe_service import validar_contenido
from src.domain.value_objects.estados import EstadoInforme, OrigenVersion


class ActualizarBorrador:
    def __init__(self, servicios: ServiciosSolicitud, informes: InformeRepository):
        self.s, self.informes = servicios, informes

    def ejecutar(self, informe_id: UUID, usuario: UsuarioActual, contenido: dict,
                numero_version: int, titulo: str | None = None):
        autorizar(usuario, escritura=True)
        validar_contenido(contenido)
        if titulo is not None and not titulo.strip():
            raise DatosInvalidos("El título no puede estar vacío")
        with self.s.uow.transaccion():
            informe = ObtenerInforme(self.s, self.informes).ejecutar(informe_id, usuario)
            if informe.estado != EstadoInforme.BORRADOR:
                raise ConflictoEstado("Solo se puede editar un informe en BORRADOR")
            actual = max(v.numero_version for v in informe.versiones)
            if numero_version != actual:
                raise ConflictoEstado("El borrador cambió; recargue su última versión")
            informe.versiones.append(VersionInforme(
                informe.id, actual + 1, contenido, OrigenVersion.USUARIO, usuario.id,
            ))
            if titulo is not None:
                informe.titulo = titulo.strip()
            informe.updated_at = ahora()
            return self.informes.guardar(informe)
