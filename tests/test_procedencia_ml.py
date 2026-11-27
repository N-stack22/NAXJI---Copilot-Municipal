import json
import pytest
from scripts.auditar_procedencia_ml import leer_csv, sin_textos
from scripts.evaluar_predictor import evaluar
from tests.test_evaluar_predictor import datos_prueba


def test_evidencia_publicable_retiene_metricas_y_excluye_sumillas():
    resultado = evaluar(datos_prueba(), medir=True)
    salida = sin_textos(resultado)
    assert salida["metricas"] == resultado["metricas"]
    assert "predicciones" not in salida
    assert datos_prueba()["casos"][0]["asunto"] not in json.dumps(salida)
    assert salida["latencia_inferencia_ms"]["p95"] >= 0


def test_no_se_reconstruyen_particiones_sobre_archivos_vacios_o_incompletos(tmp_path):
    csv = tmp_path/"datos.csv"
    for contenido in ("sumilla,tipo_informe,normativas,area_destino\n", "sumilla,tipo_informe,normativas,area_destino\ntexto,,,\n"):
        csv.write_text(contenido,encoding="utf-8")
        with pytest.raises(ValueError):
            leer_csv(csv)
