from unittest.mock import Mock
import logging

import pytest
from fastapi.testclient import TestClient

from src.adapters.out.documents.almacen_supabase import AlmacenSupabase
from src.infrastructure.configuration.settings import Settings
from src.main import create_app
from src.infrastructure import diagnostico


def test_storage_exige_https_antes_de_enviar_clave():
    with pytest.raises(ValueError):
        AlmacenSupabase("http://storage.example", "secreto-no-imprimir", "privado", 100)


@pytest.mark.parametrize("origen", ["*", "https://*.example", "https://ejemplo.test/ruta", "https://usuario:clave@ejemplo.test", "file://local"])
def test_cors_no_acepta_origenes_ambiguos(origen):
    with pytest.raises(ValueError):
        Settings(cors_origins=(origen,))


def test_documentacion_desactivable_y_salud_compatible(deps):
    with TestClient(create_app(Settings(api_docs_enabled=False), deps)) as c:
        for ruta in ("/docs", "/redoc", "/openapi.json"):
            assert c.get(ruta).status_code == 404
        assert c.get("/health").json() == {"status": "ok", "service": "NAXJI API"}


def test_cache_y_logs_no_incluyen_token_ni_identificador(client, caplog):
    iid = "11111111-1111-4111-8111-111111111111"
    with caplog.at_level(logging.WARNING):
        r = client.get(f"/solicitudes/{iid}", headers={"Authorization": "Bearer token-secreto-prueba"})
    assert r.status_code == 401
    assert r.headers["Cache-Control"] == "no-store"
    assert "ruta=/solicitudes/{solicitud_id}" in caplog.text
    assert iid not in caplog.text and "token-secreto-prueba" not in caplog.text


def test_readiness_es_privado_sanitizado_y_no_reemplaza_health(client, monkeypatch):
    monkeypatch.setattr(diagnostico.httpx, "Client", Mock(side_effect=RuntimeError("secreto")))
    assert client.get("/ready").status_code == 403
    r = client.get("/ready", headers={"Authorization": "Bearer demo-admin"})
    assert r.status_code == 503 and r.json()["comprobaciones"]["ollama"] is False
    assert "secreto" not in r.text
    assert client.get("/health").status_code == 200
