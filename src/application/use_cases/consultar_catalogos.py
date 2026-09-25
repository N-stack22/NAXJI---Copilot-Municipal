from uuid import UUID

from src.application.ports.output.catalogo_repository import CatalogoRepository
from src.application.ports.output.plantilla_repository import PlantillaRepository
from src.application.use_cases.servicios_solicitud import autorizar
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import NoEncontrado


class ConsultarCatalogos:
    def __init__(self, catalogos: CatalogoRepository, plantillas: PlantillaRepository):
        self.catalogos, self.repo_plantillas = catalogos, plantillas

    def tipos(self, usuario: UsuarioActual):
        autorizar(usuario)
        return [t for t in self.catalogos.tipos_informe() if t.activo]

    def areas(self, usuario: UsuarioActual):
        autorizar(usuario)
        return [a for a in self.catalogos.areas() if a.activo]

    def plantillas(self, usuario: UsuarioActual, tipo_informe_id: UUID | None = None):
        autorizar(usuario)
        return [p for p in self.repo_plantillas.listar()
                if p.activa and (tipo_informe_id is None or p.tipo_informe_id == tipo_informe_id)]

    def campos(self, usuario: UsuarioActual, plantilla_id: UUID):
        autorizar(usuario)
        plantilla = self.repo_plantillas.obtener_por_id(plantilla_id)
        if plantilla is None or not plantilla.activa:
            raise NoEncontrado("Plantilla activa no encontrada")
        return sorted((c for c in plantilla.campos if c.activo), key=lambda c: c.orden)
