from psycopg.types.json import Jsonb
from src.application.ports.output.revision_repository import RevisionRepository
from src.adapters.out.persistence.sql_resources import consulta
from src.domain.value_objects.estados import Rol


class RevisionPostgres(RevisionRepository):
    def __init__(self, uow):
        self.uow = uow

    def registrar(self, evento):
        with self.uow.connection(write=True) as c:
            c.execute(consulta("revision_postgres", "registrar"), (
                evento["id"], evento["informe_id"], evento["version_id"], evento["usuario_id"],
                evento["accion"], evento["estado"], evento["fecha"], Jsonb(evento["detalle"])))

    def eventos(self, informe_id):
        with self.uow.connection() as c:
            return c.execute(consulta("revision_postgres", "eventos"), (informe_id,)).fetchall()

    def listar(self, usuario, limite, desplazamiento):
        with self.uow.connection() as c:
            return c.execute(consulta("revision_postgres", "listar"), (
                Rol.ADMINISTRADOR in usuario.roles, usuario.id, Rol.REVISOR in usuario.roles,
                usuario.area_id, limite, desplazamiento)).fetchall()

    def auditoria(self, limite, desplazamiento, informe_id=None):
        with self.uow.connection() as c:
            return c.execute(consulta("revision_postgres", "auditoria"), (informe_id, informe_id, limite, desplazamiento)).fetchall()
