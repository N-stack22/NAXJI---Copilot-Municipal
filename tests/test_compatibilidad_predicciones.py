"""Lectura REST de identificadores históricos y actuales sin reescribirlos."""
import os

import pytest
from fastapi.testclient import TestClient

from src.adapters.out.ai.context_predictor_mock import ContextPredictorMock
from src.adapters.out.persistence.postgres import CatalogoRepositoryPostgres, PrediccionRepositoryPostgres, PostgresUnidadTrabajo
from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings
from src.infrastructure.dependencies import get_current_user
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.value_objects.estados import Rol
from src.main import create_app
from tests.test_estructura_postgres import db_local  # noqa: F401


@pytest.mark.parametrize("modelo", ["SKLEARN_RF_IA_01", "SKLEARN_IA_01"])
@pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL local aislado: opt-in")
def test_prediccion_historica_y_actual_se_recuperan_por_rest(db_local, modelo):
    settings, uid, _, iid, _ = db_local
    uow = PostgresUnidadTrabajo(settings)
    catalogo = CatalogoRepositoryPostgres(uow)
    with settings.connect() as c:
        sid = c.execute("SELECT solicitud_id FROM public.informes WHERE id=%s", (iid,)).fetchone()[0]
    p = ContextPredictorMock().predecir("DEMO anterior", sid)
    p.modelo = modelo
    p.tipo_informe_predicho_id = catalogo.tipos_informe()[0].id
    p.area_destino_predicha_id = catalogo.areas()[0].id
    p.normativas = []
    if modelo == "SKLEARN_IA_01":
        p.parametros["algoritmos"] = {"tipo_informe": "LogisticRegression"}
    PrediccionRepositoryPostgres(uow).guardar(p)
    config = Settings(persistence_mode="postgres", auth_mode="disabled")
    deps = Container(config, database_settings=settings)
    app = create_app(config, deps)
    app.dependency_overrides[get_current_user] = lambda: UsuarioActual(uid, frozenset({Rol.FUNCIONARIO}))
    with TestClient(app) as client:
        r = client.get(f"/solicitudes/{sid}/contexto")
        assert r.status_code == 200, r.text
        assert r.json()["modelo"] == modelo
        assert r.json()["es_mock"] is False
        assert r.json()["algoritmos"] == p.parametros.get("algoritmos", {})
    recuperada = PrediccionRepositoryPostgres(PostgresUnidadTrabajo(settings)).ultima(sid)
    assert recuperada.modelo == modelo
    assert recuperada.parametros == p.parametros
