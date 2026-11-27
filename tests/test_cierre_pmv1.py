from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest

from src.adapters.out.ai.context_predictor_catalogo import ContextPredictorCatalogo
from src.adapters.out.ai.context_predictor_mock import ContextPredictorMock
from src.adapters.out.ai.integridad_modelos import HUELLAS, verificar_artefactos
from src.adapters.out.persistence.datos_demo import AREAS, TIPOS, demo_id
from src.application.ports.input.solicitud_use_case import DatosSolicitud
from src.domain.services.errores import DatosInvalidos
from src.domain.value_objects.estados import ResultadoValidacion


def test_area_sin_correspondencia_no_inventa_destino_y_exige_correccion(deps, usuario):
    areas = [replace(a, codigo='MDT_SGGA') for a in AREAS[:1]]
    catalogos = Mock()
    catalogos.areas.return_value = areas
    catalogos.tipos_informe.return_value = TIPOS
    catalogos.correspondencias_normativas.return_value = []
    catalogos.normativa.return_value = None
    predictor = Mock()
    prediccion = ContextPredictorMock().predecir('Prueba', uuid4())
    prediccion.area_destino_predicha_id = demo_id('AREA_RIESGO_DESASTRES')
    prediccion.normativas = []
    predictor.predecir.return_value = prediccion
    adaptado = ContextPredictorCatalogo(predictor, catalogos)
    resultado = adaptado.predecir('Prueba', prediccion.solicitud_id)
    assert resultado.area_destino_predicha_id is None
    assert resultado.parametros['area_pendiente_confirmacion'] is True
    assert resultado.parametros['advertencias_catalogo']
    deps.servicios.catalogos = catalogos
    solicitud = deps.crear_solicitud.ejecutar(usuario, DatosSolicitud('Prueba'))
    resultado.solicitud_id = solicitud.id
    resultado.area_destino_predicha_id = demo_id('AREA_RIESGO_DESASTRES')
    deps.predecir_contexto.predictor = adaptado
    p = deps.predecir_contexto.ejecutar(solicitud.id, usuario)
    with pytest.raises(DatosInvalidos, match='CORREGIDA'):
        deps.validar_prediccion.ejecutar(solicitud.id, usuario, p.id, ResultadoValidacion.ACEPTADA)
    deps.validar_prediccion.ejecutar(solicitud.id, usuario, p.id, ResultadoValidacion.CORREGIDA, TIPOS[0].id, areas[0].id, [])
    assert deps.solicitudes.obtener_por_id(solicitud.id).area_destino_id == areas[0].id


def test_huellas_detectan_modificacion_antes_de_deserializar(tmp_path):
    original = Path(__file__).resolve().parents[1] / 'src/infrastructure/ai/models'
    for nombre in HUELLAS:
        (tmp_path / nombre).write_bytes((original / nombre).read_bytes())
    verificar_artefactos(tmp_path)
    (tmp_path / 'modelo_tipo.joblib').write_bytes(b'alterado')
    with pytest.raises(ValueError, match='huella'):
        verificar_artefactos(tmp_path)
