from uuid import uuid4

import pytest

from src.domain.entities.plantilla import CampoPlantilla
from src.domain.services.errores import DatosInvalidos
from src.domain.services.solicitud_service import SolicitudService
from src.domain.value_objects.estados import TipoDato


@pytest.mark.parametrize("tipo,valor", [
    (TipoDato.TEXT, 123), (TipoDato.TEXTAREA, "  "),
    (TipoDato.DATE, "2026-02-30"), (TipoDato.DATE, "20260925"),
    (TipoDato.NUMBER, True), (TipoDato.NUMBER, float("nan")),
    (TipoDato.BOOLEAN, 1), (TipoDato.SELECT, "OTRO"),
])
def test_valores_invalidos(tipo, valor):
    campo = CampoPlantilla(uuid4(), uuid4(), "dato", "Dato", tipo, True, 1, {"opciones": ["NORMAL"]})
    with pytest.raises(DatosInvalidos):
        SolicitudService.validar_valor(campo, valor)


@pytest.mark.parametrize("tipo,valor", [
    (TipoDato.TEXT, "Texto"), (TipoDato.TEXTAREA, "Antecedentes"),
    (TipoDato.DATE, "2026-09-25"), (TipoDato.NUMBER, 0),
    (TipoDato.BOOLEAN, False), (TipoDato.SELECT, "NORMAL"),
])
def test_valores_validos_incluyen_cero_y_false(tipo, valor):
    campo = CampoPlantilla(uuid4(), uuid4(), "dato", "Dato", tipo, True, 1, {"opciones": ["NORMAL"]})
    SolicitudService.validar_valor(campo, valor)
