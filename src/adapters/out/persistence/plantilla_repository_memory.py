from copy import deepcopy
from uuid import UUID

from src.adapters.out.persistence.datos_demo import plantillas_demo
from src.application.ports.output.plantilla_repository import PlantillaRepository


class PlantillaRepositoryMemory(PlantillaRepository):
    def __init__(self):
        self.plantillas = {p.id: p for p in plantillas_demo()}

    def listar(self):
        return deepcopy([p for p in self.plantillas.values() if p.activa])

    def obtener_por_id(self, plantilla_id: UUID):
        return deepcopy(self.plantillas.get(plantilla_id))
