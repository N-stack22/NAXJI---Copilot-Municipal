from uuid import uuid4
from src.application.ports.output.informe_repository import InformeRepository
from src.domain.entities.solicitud import ahora


class InformeAuditado(InformeRepository):
    """El informe y su evento se escriben en una única unidad de trabajo."""
    def __init__(self, informes, revisiones, uow):
        self.base, self.revisiones, self.uow = informes, revisiones, uow

    def obtener_por_id(self, informe_id):
        return self.base.obtener_por_id(informe_id)

    def obtener_por_solicitud(self, solicitud_id):
        return self.base.obtener_por_solicitud(solicitud_id)

    def guardar(self, informe):
        with self.uow.transaccion():
            anterior = self.base.obtener_por_id(informe.id)
            existentes = {v.id for v in anterior.versiones} if anterior else set()
            guardado = self.base.guardar(informe)
            for version in guardado.versiones:
                if version.id not in existentes:
                    self.revisiones.registrar({"id": uuid4(), "informe_id": informe.id, "version_id": version.id,
                        "usuario_id": version.creado_por, "accion": "CREAR_VERSION", "estado": guardado.estado.value,
                        "fecha": ahora(), "detalle": {"numero_version": version.numero_version}})
            return guardado
