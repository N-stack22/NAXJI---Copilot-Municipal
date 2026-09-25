from copy import deepcopy
from uuid import UUID

from src.adapters.out.persistence.datos_demo import AREAS, NORMATIVA, TIPOS
from src.application.ports.output.catalogo_repository import CatalogoRepository


class CatalogoRepositoryMemory(CatalogoRepository):
    def tipos_informe(self):
        return deepcopy(TIPOS)

    def areas(self):
        return deepcopy(AREAS)

    def normativa(self, normativa_id: UUID):
        return deepcopy(NORMATIVA) if normativa_id == NORMATIVA.id else None
