"""Datos sintéticos solo para verificar la herramienta, nunca métricas oficiales."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.evaluar_predictor import evaluar, metricas_categoria, metricas_temas, validar_datos


def datos_prueba():
    return {"metadata": {"fuente": "Prueba unitaria sintética", "etiquetado": "Fixture de software",
                         "particion": "test_herramienta", "independiente_entrenamiento": False},
            "casos": [{"id": "prueba-1", "asunto": "Inspección de parque de prueba",
                       "tipo_informe": "Informe de Inspección",
                       "area_destino": "Subgerencia de Ecología y Medio Ambiente", "temas_normativos": []}]}


def test_metricas_categoria_con_errores_y_clase_sin_soporte():
    r = metricas_categoria(["a", "b"], ["a", "a"], ["a", "b", "c"])
    assert r["accuracy"] == 0.5
    assert r["matriz_confusion"] == [[1, 0, 0], [1, 0, 0], [0, 0, 0]]
    assert r["por_clase_y_promedios"]["a"]["precision"] == 0.5
    assert r["por_clase_y_promedios"]["b"]["recall"] == 0
    assert r["por_clase_y_promedios"]["c"]["support"] == 0


def test_metricas_multietiqueta_no_confunden_acierto_parcial_con_conjunto_exacto():
    r = metricas_temas([["a", "b"], []], [["a"], []], ["a", "b"])
    assert r["accuracy_conjunto_exacto"] == 0.5
    assert r["hamming_loss"] == 0.25
    assert r["promedios"]["micro"]["precision"] == 1
    assert r["promedios"]["micro"]["recall"] == 0.5
    assert r["promedios"]["micro"]["f1"] == pytest.approx(2 / 3)


@pytest.mark.parametrize("defecto", ["vacio", "duplicado", "asunto_repetido", "sin_etiqueta", "tipo_desconocido", "tema_desconocido", "tema_repetido", "sin_procedencia"])
def test_rechaza_evaluaciones_invalidas(defecto):
    datos = datos_prueba()
    if defecto == "vacio": datos["casos"] = []
    elif defecto == "duplicado": datos["casos"] *= 2
    elif defecto == "asunto_repetido": datos["casos"].append({**deepcopy(datos["casos"][0]), "id": "otra"})
    elif defecto == "sin_etiqueta": del datos["casos"][0]["area_destino"]
    elif defecto == "tipo_desconocido": datos["casos"][0]["tipo_informe"] = "Inventado"
    elif defecto == "tema_desconocido": datos["casos"][0]["temas_normativos"] = ["Inventado"]
    elif defecto == "tema_repetido": datos["casos"][0]["temas_normativos"] = ["a", "a"]
    else: del datos["metadata"]["fuente"]
    with pytest.raises(ValueError):
        validar_datos(datos, ["a", "b"])


def test_evaluacion_real_es_reproducible_y_no_certifica_independencia():
    r = evaluar(datos_prueba())
    assert r == evaluar(datos_prueba())
    assert r["independencia_verificada"] is False
    assert r["numero_casos"] == 1
    assert r["predicciones"][0]["modelo"] == "SKLEARN_IA_01"
    assert r["metricas"]["tipo_informe"]["por_clase_y_promedios"]["Memorando"]["support"] == 0


def test_cli_genera_hashes_y_no_sobrescribe_evidencia(tmp_path):
    entrada, salida = tmp_path / "datos.json", tmp_path / "resultado.json"
    entrada.write_text(json.dumps(datos_prueba()), encoding="utf-8")
    comando = [sys.executable, "scripts/evaluar_predictor.py", "--datos", str(entrada), "--salida", str(salida)]
    r = subprocess.run(comando, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    original = salida.read_bytes()
    informe = json.loads(original)
    assert len(informe["sha256_artefactos"]) == 6
    assert len(informe["sha256_datos"]) == 64
    assert subprocess.run(comando, capture_output=True).returncode == 2
    assert salida.read_bytes() == original
    # Un metadato no serializable como JSON no debe dejar evidencia parcial.
    datos = datos_prueba()
    datos["metadata"]["valor_invalido"] = float("nan")
    entrada.write_text(json.dumps(datos), encoding="utf-8")
    comando[-1] = str(tmp_path / "no_crear.json")
    assert subprocess.run(comando, capture_output=True).returncode == 2
    assert not Path(comando[-1]).exists()
