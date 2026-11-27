"""La extraccion de SQL debe ser independiente del directorio de ejecucion."""
import ast
from pathlib import Path
import re

from src.adapters.out.persistence.sql_resources import consulta


ROOT = Path(__file__).resolve().parents[1]
PERSISTENCE = ROOT / "src/adapters/out/persistence"
SQL = re.compile(
    r"\b(?:SELECT\s+(?:\*|\d|[\w\"(])|INSERT\s+INTO\b|UPDATE\s+\S+\s+SET\b|"
    r"DELETE\s+FROM\b|(?:CREATE|ALTER|DROP|TRUNCATE)\s+(?:TABLE|INDEX|SCHEMA|EXTENSION)\b|"
    r"WITH\s+\w+\s+AS\s*\(|SET\s+(?:LOCAL\s+|TRANSACTION\s+)?\w+\s*(?:=|TO\b|ISOLATION\b)|"
    r"FOR\s+UPDATE\b|ON\s+CONFLICT\b|(?:FROM|JOIN)\s+[\w\"]+|WHERE\s+[\w\"]+\s*(?:=|IN\b)|"
    r"ORDER\s+BY\b|RETURNING\s+(?:\*|\w))", re.I | re.S)


def adaptadores(carpeta=PERSISTENCE):
    return sorted(carpeta.rglob("*.py"))


def texto_fijo(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(texto_fijo(v) if isinstance(v, ast.Constant) else "identificador" for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return texto_fijo(node.left) + texto_fijo(node.right)
    return ""


def sql_incrustado(archivo):
    tree = ast.parse(archivo.read_text(encoding="utf-8-sig"))
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                  and n.body and isinstance(n.body[0], ast.Expr)
                  and isinstance(n.body[0].value, ast.Constant)}
    for node in ast.walk(tree):
        if id(node) in docstrings:
            continue
        texto = re.sub(r"/\*.*?\*/|--[^\n]*", " ", texto_fijo(node), flags=re.S)
        if SQL.search(texto):
            yield node.lineno


def consultas_referenciadas(archivo):
    tree = ast.parse(archivo.read_text(encoding="utf-8-sig"))
    aliases = {"consulta"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").endswith("sql_resources"):
            aliases.update(a.asname or a.name for a in node.names if a.name == "consulta")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and ((isinstance(node.func, ast.Name) and node.func.id in aliases)
                                           or isinstance(node.func, ast.Attribute) and node.func.attr == "consulta"):
            assert len(node.args) == 2 and all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args), (archivo, node.lineno)
            yield tuple(a.value for a in node.args)


def test_adaptadores_no_contienen_sentencias_sql_en_python():
    errores = [(str(p.relative_to(ROOT)), linea) for p in adaptadores() for linea in sql_incrustado(p)]
    assert not errores, errores


def test_todas_las_consultas_referenciadas_son_recursos_legibles_fuera_del_repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    consulta.cache_clear()
    referenced = {r for p in adaptadores() for r in consultas_referenciadas(p)}
    for adapter, query in referenced:
        assert consulta(adapter, query)
    base = PERSISTENCE / "sql"
    packaged = {(p.parent.relative_to(base).as_posix(), p.stem) for p in base.rglob("*.sql")}
    assert referenced == packaged  # Ni consultas faltantes ni recursos huerfanos.


import pytest


@pytest.mark.parametrize("codigo", [
    'q = "SELECT 1"', 'db.execute("-- consulta\\nSELECT * FROM documentos")',
    'q = f"SELECT * FROM {tabla}"', 'q = "SEL" + "ECT * FROM documentos"',
    'q = "/* comentario */ INSERT INTO documentos VALUES (%s)"',
    'q = "UPDATE documentos SET titulo=%s"', 'q = "DELETE FROM documentos"',
    'q = "WITH fuentes AS (SELECT 1) SELECT * FROM fuentes"',
    'q = "CREATE TABLE nueva(id uuid)"', 'q = " FOR UPDATE"',
    'q = " ORDER BY distancia LIMIT 6"',
])
def test_guardia_descubre_sql_en_adaptador_nuevo_anidado(tmp_path, codigo):
    archivo = tmp_path / "nuevo/subdirectorio/repositorio.py"
    archivo.parent.mkdir(parents=True)
    archivo.write_text(codigo, encoding="utf-8")
    assert archivo in adaptadores(tmp_path)
    assert list(sql_incrustado(archivo))


def test_composicion_segura_y_alias_de_recursos_no_son_sql_incrustado(tmp_path):
    archivo = tmp_path / "nuevo.py"
    archivo.write_text('from .sql_resources import consulta as query\n'
                       'statement = sql.SQL(query("postgres", "save_insert")).format(sql.Identifier(table))\n'
                       'separator = sql.SQL(", ")', encoding="utf-8")
    assert not list(sql_incrustado(archivo))
    assert list(consultas_referenciadas(archivo)) == [("postgres", "save_insert")]
