from copy import deepcopy
import importlib
from uuid import uuid4
from src.domain.entities.informe import Informe, VersionInforme
from src.domain.value_objects.estados import OrigenVersion


def test_presentacion_respeta_snapshot_ante_jsonb_desordenado_y_conserva_extras():
    representar = importlib.import_module("src.adapters.in.schemas.informe_response").representar_informe
    informe = Informe(uuid4(), uuid4(), uuid4())
    contenido = {"conclusiones":"C", "extra_historica":"X", "encabezado":{}, "desarrollo":"D", "antecedentes":"A"}
    original = deepcopy(contenido)
    informe.versiones = [VersionInforme(informe.id, 1, contenido, OrigenVersion.IA, informe.creado_por)]
    salida = representar(informe)
    assert list(salida.contenido)[:3] == ["antecedentes", "desarrollo", "conclusiones"]
    assert salida.contenido == original
    assert list(informe.versiones[0].contenido) == list(original)
