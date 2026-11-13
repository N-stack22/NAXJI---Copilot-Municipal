"""Consulta real de perfiles/roles en una base nueva del cluster aislado."""
import os
from uuid import uuid4

import pytest

from src.adapters.out.persistence.perfil_repository_postgres import PerfilRepositoryPostgres
from src.adapters.out.persistence.postgres import PostgresUnidadTrabajo
from src.domain.value_objects.estados import Rol
from tests.test_estructura_postgres import db_local  # noqa: F401


pytestmark = pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL local aislado: opt-in")


def test_perfil_conserva_area_roles_activos_y_perfil_inactivo(db_local):
    settings, uid, _, _, _ = db_local
    with settings.connect() as c:
        area_id, area_nombre = c.execute("SELECT id,nombre FROM public.areas_municipales ORDER BY codigo LIMIT 1").fetchone()
        c.execute("UPDATE public.perfiles SET area_id=%s,cargo='Cargo QA',activo=false WHERE id=%s", (area_id, uid))
        c.execute("INSERT INTO public.roles(codigo,nombre) VALUES ('ROL_DESCONOCIDO','Desconocido')")
        c.execute("UPDATE public.roles SET activo=false WHERE codigo='REVISOR'")
        c.execute("INSERT INTO public.usuario_roles(usuario_id,rol_id) SELECT %s,id FROM public.roles WHERE codigo IN ('FUNCIONARIO','REVISOR','ROL_DESCONOCIDO')", (uid,))
    repo = PerfilRepositoryPostgres(PostgresUnidadTrabajo(settings))
    user = repo.obtener_usuario(uid, 'qa@example.invalid')
    assert user.id == uid and user.roles == frozenset({Rol.FUNCIONARIO})
    assert (user.area_id, user.area_nombre, user.cargo, user.email, user.activo) == (area_id, area_nombre, 'Cargo QA', 'qa@example.invalid', False)
    assert repo.obtener_usuario(uuid4(), 'missing@example.invalid') is None
