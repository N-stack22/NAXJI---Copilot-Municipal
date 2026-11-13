from src.adapters.out.persistence.sql_resources import consulta
from src.application.ports.output.perfil_repository import PerfilRepository
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.value_objects.estados import Rol


class PerfilRepositoryPostgres(PerfilRepository):
    def __init__(self, uow):
        self.uow = uow

    def obtener_usuario(self, usuario_id, email):
        with self.uow.connection() as c:
            perfil = c.execute(
                consulta("perfil_repository_postgres", "obtener_perfil"),
                (usuario_id,),
            ).fetchone()
            if perfil is None:
                return None
            roles = c.execute(
                consulta("perfil_repository_postgres", "obtener_roles"), (usuario_id,),
            ).fetchall()
            known = {r.value for r in Rol}
            return UsuarioActual(
                id=usuario_id, roles=frozenset(Rol(r["codigo"]) for r in roles if r["codigo"] in known),
                area_id=perfil["area_id"], activo=perfil["activo"], email=email,
                nombres=perfil["nombres"], apellidos=perfil["apellidos"], cargo=perfil["cargo"],
                area_nombre=perfil["area_nombre"],
            )
