from abc import ABC, abstractmethod


class RevisionRepository(ABC):
    """Eventos inmutables de revisión y consultas acotadas por identidad/área."""

    @abstractmethod
    def registrar(self, evento: dict): ...

    @abstractmethod
    def eventos(self, informe_id): ...

    @abstractmethod
    def listar(self, usuario, limite, desplazamiento): ...

    @abstractmethod
    def auditoria(self, limite, desplazamiento, informe_id=None): ...
