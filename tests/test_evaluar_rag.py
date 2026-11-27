from copy import deepcopy
import pytest
from scripts.evaluar_rag import evaluar


CORPUS = {"documentos": [{"id": "a"}, {"id": "b"}],
          "consultas": [{"id": "q1", "relevantes": ["b"]}, {"id": "q2", "relevantes": []}]}


def test_metricas_cuentan_fallos_ranking_y_rechazo_sin_division_por_cero():
    r = evaluar(CORPUS, [[1., 0], [.8, .6]], [[1., 0], [-1., 0]], .5, 2)
    assert r["hit_at_1"] == 0 and r["hit_at_k"] == 1
    assert r["mrr_at_k"] == .5
    assert r["macro_precision_at_k"] == .5 and r["macro_recall_at_k"] == 1
    assert r["rechazo_negativas"] == 1
    corpus = deepcopy(CORPUS); corpus["consultas"] = [corpus["consultas"][1]]
    r = evaluar(corpus, [[1., 0], [.8, .6]], [[-1., 0]], .5, 1)
    assert r["hit_at_k"] is None and r["rechazo_negativas"] == 1


@pytest.mark.parametrize("defecto", ["dimensiones", "faltantes", "nan", "ground_truth", "duplicado", "cero_k"])
def test_no_calcula_metricas_sobre_datos_incompatibles(defecto):
    corpus = deepcopy(CORPUS); docs = [[1., 0], [0, 1.]]; consultas = [[1., 0], [-1., 0]]; k = 1
    if defecto == "dimensiones": docs[0] = [1.]
    elif defecto == "faltantes": consultas.pop()
    elif defecto == "nan": docs[0][0] = float("nan")
    elif defecto == "ground_truth": corpus["consultas"][0]["relevantes"] = ["inexistente"]
    elif defecto == "duplicado": corpus["documentos"][1]["id"] = "a"
    else: k = 0
    with pytest.raises(ValueError):
        evaluar(corpus, docs, consultas, .5, k)
