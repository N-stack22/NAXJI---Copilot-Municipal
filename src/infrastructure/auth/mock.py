"""Identidades temporales; no crea usuarios ni persiste credenciales."""
from src.adapters.out.persistence.datos_demo import AREAS, demo_id
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.value_objects.estados import Rol


def usuarios_demo() -> dict[str, UsuarioActual]:
    return {
        "demo-funcionario": UsuarioActual(demo_id("usuario"), frozenset({Rol.FUNCIONARIO}), AREAS[0].id),
        "demo-otro": UsuarioActual(demo_id("otro-usuario"), frozenset({Rol.FUNCIONARIO}), AREAS[1].id),
        "demo-revisor": UsuarioActual(demo_id("usuario"), frozenset({Rol.REVISOR}), AREAS[0].id),
        "demo-aprobador": UsuarioActual(demo_id("usuario"), frozenset({Rol.APROBADOR}), AREAS[0].id),
        "demo-admin": UsuarioActual(demo_id("admin"), frozenset({Rol.ADMINISTRADOR}), AREAS[0].id),
    }
