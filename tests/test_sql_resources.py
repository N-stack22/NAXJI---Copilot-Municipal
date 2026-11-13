"""La extraccion de SQL debe ser independiente del directorio de ejecucion."""
import ast
from pathlib import Path
import re

from src.adapters.out.persistence.sql_resources import consulta


ROOT = Path(__file__).resolve().parents[1]
PERSISTENCE = ROOT / "src/adapters/out/persistence"
ADAPTERS = ("documentos_postgres", "postgres", "perfil_repository_postgres")


def test_adaptadores_no_contienen_sentencias_sql_en_python():
    sentencia = re.compile(r"^\s*(SELECT|INSERT|UPDATE|DELETE|SET|WITH|FOR UPDATE|ON CONFLICT)\b", re.I)
    for name in ADAPTERS:
        tree = ast.parse((PERSISTENCE / (name + ".py")).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert not sentencia.match(node.value), (name, node.lineno)


def test_todas_las_consultas_referenciadas_son_recursos_legibles_fuera_del_repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    consulta.cache_clear()
    referenced = set()
    for name in ADAPTERS:
        tree = ast.parse((PERSISTENCE / (name + ".py")).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "consulta":
                adapter, query = (arg.value for arg in node.args)
                assert consulta(adapter, query)
                referenced.add((adapter, query))
    packaged = {(p.parent.name, p.stem) for p in (PERSISTENCE / "sql").glob("*/*.sql")}
    assert referenced == packaged  # Ni consultas faltantes ni recursos huerfanos.
