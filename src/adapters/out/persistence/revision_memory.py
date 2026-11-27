from copy import deepcopy
from src.application.ports.output.revision_repository import RevisionRepository
from src.domain.value_objects.estados import Rol


class RevisionMemory(RevisionRepository):
    def __init__(self, memoria):
        self.memoria = memoria

    def registrar(self, evento):
        with self.memoria.lock:
            self.memoria.revisiones.append(deepcopy(evento))

    def eventos(self, informe_id):
        with self.memoria.lock:
            return deepcopy([e for e in self.memoria.revisiones if e["informe_id"] == informe_id])

    def listar(self, usuario, limite, desplazamiento):
        with self.memoria.lock:
            items = []
            for informe in self.memoria.informes.values():
                solicitud = self.memoria.solicitudes[informe.solicitud_id]
                if (Rol.ADMINISTRADOR in usuario.roles or solicitud.usuario_id == usuario.id
                    or (Rol.REVISOR in usuario.roles and usuario.area_id is not None
                        and usuario.area_id == solicitud.area_destino_id)):
                    items.append({"id": informe.id, "titulo": informe.titulo, "estado": informe.estado,
                                  "creado_por": informe.creado_por, "fecha": informe.created_at})
            items.sort(key=lambda i: (i["fecha"], str(i["id"])), reverse=True)
            return deepcopy(items[desplazamiento:desplazamiento+limite])

    def auditoria(self, limite, desplazamiento, informe_id=None):
        with self.memoria.lock:
            items = [e for e in reversed(self.memoria.revisiones) if informe_id is None or e["informe_id"] == informe_id]
            return deepcopy(items[desplazamiento:desplazamiento+limite])
