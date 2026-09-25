from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.catalogo import AreaMunicipal, Normativa, TipoInforme


class CatalogoRepository(ABC):
    @abstractmethod
    def tipos_informe(self) -> list[TipoInforme]: ...

    @abstractmethod
    def areas(self) -> list[AreaMunicipal]: ...

    @abstractmethod
    def normativa(self, normativa_id: UUID) -> Normativa | None: ...
