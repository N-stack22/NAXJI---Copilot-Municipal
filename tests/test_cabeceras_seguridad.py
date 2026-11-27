"""Regresiones del hallazgo ZAP confirmado en respuestas normales y errores."""
from fastapi.testclient import TestClient
import pytest
from pathlib import Path


@pytest.mark.parametrize("metodo,ruta,kwargs,status", [
    ("GET", "/health", {}, 200),
    ("GET", "/auth/me", {"headers": {"Authorization": ""}}, 401),
    ("GET", "/ruta-inexistente", {}, 404),
    ("POST", "/solicitudes", {"json": {}}, 422),
])
def test_nosniff_cubre_respuestas_y_errores(client, metodo, ruta, kwargs, status):
    response = client.request(metodo, ruta, **kwargs)
    assert response.status_code == status
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_error_no_controlado_conserva_nosniff_y_no_expone_excepcion(client):
    @client.app.get("/fallo-de-prueba")
    def fallo():
        raise RuntimeError("detalle privado ficticio")
    response = client.get("/fallo-de-prueba")
    assert response.status_code == 500
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "detalle privado" not in response.text


def test_politica_estatica_no_permite_scripts_inline_y_cierra_marcos():
    contenido = (Path(__file__).resolve().parents[1] / "public/_headers").read_text()
    assert "script-src 'self'" in contenido
    assert "'unsafe-inline'" not in contenido and "'unsafe-eval'" not in contenido
    assert "frame-ancestors 'none'" in contenido
    assert "X-Frame-Options: DENY" in contenido
    assert "connect-src 'self' https://naxji-production.up.railway.app" in contenido
