from copy import deepcopy
from uuid import UUID

from src.adapters.out.persistence.datos_demo import (
    AREAS,
    NORMATIVAS,
    TIPOS,
)
from src.application.ports.output.catalogo_repository import (
    CatalogoRepository,
)


class CatalogoRepositoryMemory(
    CatalogoRepository
):

    def tipos_informe(self):
        return deepcopy(TIPOS)

    def areas(self):
        return deepcopy(AREAS)

    def normativa(
        self,
        normativa_id: UUID
    ):
        normativa = next(
            (
                n
                for n in NORMATIVAS
                if n.id == normativa_id
            ),
            None
        )

        return deepcopy(normativa)