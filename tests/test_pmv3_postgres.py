"""PostgreSQL desechable: migración aditiva, decisiones atómicas y bloqueo entre instancias."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings
from src.adapters.out.ai.context_predictor_mock import ContextPredictorMock
from src.adapters.out.ai.generador_borrador_mock import GeneradorBorradorMock
from src.adapters.out.persistence.postgres import PersistenceError
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import ConflictoEstado
from src.domain.value_objects.estados import Rol
from tests.test_estructura_postgres import db_local  # noqa: F401
from tests.test_pmv3 import comprobaciones

pytestmark = pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL local aislado: opt-in")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def revision_db(db_local):
    config, uid, _, iid, _ = db_local
    with config.connect(autocommit=True) as c:
        anteriores = c.execute("SELECT to_jsonb(v) FROM versiones_informe v ORDER BY id").fetchall()
        for _ in range(2):
            c.execute((ROOT / "database/migrations/20261126_01_pmv3_revision.sql").read_text(encoding="utf-8"))
            assert c.execute("SELECT to_jsonb(v) FROM versiones_informe v ORDER BY id").fetchall() == anteriores
        area = c.execute("SELECT id FROM areas_municipales LIMIT 1").fetchone()[0]
        c.execute("UPDATE solicitudes SET area_destino_id=%s WHERE id=(SELECT solicitud_id FROM informes WHERE id=%s)", (area, iid))
        rid = uuid4()
        c.execute("INSERT INTO auth.users VALUES (%s)", (rid,))
        c.execute("INSERT INTO perfiles(id,nombres,apellidos) VALUES (%s,'Revisor','Prueba')", (rid,))
    def nuevo():
        return Container(Settings(persistence_mode="postgres", auth_mode="disabled", pmv3_enabled=True), database_settings=config,
                         predictor=ContextPredictorMock(), generador=GeneradorBorradorMock())
    yield config, nuevo, iid, UsuarioActual(uid, frozenset({Rol.FUNCIONARIO}), area), UsuarioActual(rid, frozenset({Rol.REVISOR}), area)


def test_dos_instancias_deciden_una_vez_y_persisten_historia(revision_db):
    cfg, nuevo, iid, autor, revisor = revision_db
    d, otro = nuevo(), nuevo()
    h = d.revision.enviar(iid, autor, 1)
    contenido_original = h["versiones"][0]["contenido"]
    contenido = {s["clave"]: "Contenido editado por el revisor" for s in h["versiones"][0]["secciones"]}
    h = d.revision.editar(iid, revisor, 1, contenido)
    assert otro.revision.historial(iid, autor)["versiones"][0]["contenido"] == contenido_original
    def decidir(deps):
        try:
            deps.revision.decidir(iid, revisor, 2, "APROBADO", "Comprobación humana", comprobaciones(h))
            return "ok"
        except ConflictoEstado:
            return "conflicto"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(decidir, [d, otro])) == ["conflicto", "ok"]
    assert nuevo().revision.historial(iid, autor)["estado"] == "APROBADO"
    assert otro.revision.exportar(iid, 2, autor, "pdf").startswith(b"%PDF")
    with cfg.connect() as c:
        assert c.execute("SELECT count(*) FROM revision_eventos WHERE accion='APROBADO'").fetchone()[0] == 1
    for operacion in ("UPDATE revision_eventos SET estado='BORRADOR'", "DELETE FROM revision_eventos"):
        with pytest.raises(psycopg.Error, match="inmutables"):
            with cfg.connect() as c:
                c.execute(operacion)


def test_fallo_auditoria_revierte_edicion_y_estado_postgres(revision_db):
    cfg, nuevo, iid, autor, revisor = revision_db
    d = nuevo()
    h = d.revision.enviar(iid, autor, 1)
    with cfg.connect() as c:
        c.execute("CREATE FUNCTION fallo_evento() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'fallo de prueba'; END $$")
        c.execute("CREATE TRIGGER fallo_evento BEFORE INSERT ON revision_eventos FOR EACH ROW EXECUTE FUNCTION fallo_evento()")
    with pytest.raises(PersistenceError):
        d.revision.decidir(iid, revisor, 1, "APROBADO", "Prueba", comprobaciones(h))
    assert nuevo().revision.historial(iid, autor)["estado"] == "EN_REVISION"
    with pytest.raises(PersistenceError):
        d.revision.editar(iid, revisor, 1, {s["clave"]: "Texto de prueba" for s in h["versiones"][0]["secciones"]})
    assert len(nuevo().revision.historial(iid, autor)["versiones"]) == 1
    with cfg.connect() as c:
        c.execute("DROP TRIGGER fallo_evento ON revision_eventos; DROP FUNCTION fallo_evento()")


def test_permisos_listados_y_auditoria_en_postgres(revision_db):
    _, nuevo, iid, autor, revisor = revision_db
    d = nuevo()
    # Los registros previos a PMV3 no tienen historia de estado: no se inventa.
    assert d.revision.historial(iid, autor)["versiones"][0]["estado"] == "NO_REGISTRADO"
    d.revision.enviar(iid, autor, 1)
    assert d.revision.listar(replace(revisor, area_id=uuid4())) == []
    assert d.revision.listar(revisor, 1)[0]["id"] == iid
    assert d.revision.listar(autor, 1, 1) == []
    admin = replace(revisor, roles=frozenset({Rol.ADMINISTRADOR}))
    assert d.revision.auditoria(admin, informe_id=iid)[0]["usuario_id"] == autor.id
