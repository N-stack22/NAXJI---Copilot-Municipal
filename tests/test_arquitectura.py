"""Reglas sobre todos los módulos; resuelve también imports relativos y alias."""
import ast
import importlib
from importlib.util import resolve_name
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def nombre_modulo(archivo, root=ROOT):
    partes = archivo.relative_to(root).with_suffix("").parts
    return ".".join(partes[:-1] if partes[-1] == "__init__" else partes)


def dependencias(archivo, root=ROOT):
    modulo = nombre_modulo(archivo, root)
    paquete = modulo if archivo.name == "__init__.py" else modulo.rpartition(".")[0]
    tree = ast.parse(archivo.read_text(encoding="utf-8-sig"))
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name] = alias.name
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom):
            base = resolve_name("." * node.level + (node.module or ""), paquete) if node.level else node.module or ""
            yield node.lineno, base
            for alias in node.names:
                target = f"{base}.{alias.name}"
                aliases[alias.asname or alias.name] = target
                p = root.joinpath(*target.split("."))
                if p.with_suffix(".py").is_file() or p.is_dir():
                    yield node.lineno, target
        elif isinstance(node, ast.Call):
            llamado = ast.unparse(node.func)
            cabecera, _, cola = llamado.partition(".")
            llamado = aliases.get(cabecera, cabecera) + ("." + cola if cola else "")
            if llamado in {"importlib.import_module", "__import__"}:
                if not node.args or not isinstance(node.args[0], ast.Constant):
                    if modulo.startswith(("src.domain", "src.application")):
                        raise AssertionError(f"{archivo}:{node.lineno}: import dinámico no comprobable")
                    continue  # La composición exterior se comprueba además importando todos los módulos.
                target = node.args[0].value
                if isinstance(target, str):
                    yield node.lineno, resolve_name(target, paquete) if target.startswith(".") else target


def infracciones(archivo, root=ROOT):
    modulo = nombre_modulo(archivo, root)
    permitidos = ("src.domain",) if modulo.startswith("src.domain") else ("src.domain", "src.application")
    for linea, target in dependencias(archivo, root):
        if not modulo.startswith(("src.domain", "src.application")):
            continue
        if target == "src":
            continue  # El submódulo importado se comprueba por separado.
        if target.startswith("src."):
            valido = any(target == p or target.startswith(p + ".") for p in permitidos)
        else:
            valido = target.split(".")[0] in sys.stdlib_module_names
        if not valido:
            yield f"{modulo}:{linea} -> {target}"


def test_dependencias_de_todos_los_modulos_respetan_las_capas():
    errores = []
    for archivo in sorted(SRC.rglob("*.py")):
        list(dependencias(archivo))  # Resuelve también todos los imports exteriores.
        errores.extend(infracciones(archivo))
    assert not errores, "\n".join(errores)


def test_todos_los_modulos_se_importan_sin_servicios_externos():
    for archivo in sorted(SRC.rglob("*.py")):
        importlib.import_module(nombre_modulo(archivo))


@pytest.mark.parametrize("sentencia", [
    "from ...application.use_cases import servicio", "from src import application",
    "from ... import application", "import src.application as app",
    "from ...adapters import out", "from ...infrastructure import dependencies",
    "from importlib import import_module as cargar\ncargar('src.application')",
    "import importlib as imp\nimp.import_module('src.adapters')",
    "__import__('src.infrastructure')", "from fastapi import FastAPI",
])
def test_guardia_detecta_dependencias_prohibidas_incluso_relativas(tmp_path, sentencia):
    archivo = tmp_path / "src/domain/services/ejemplo.py"
    archivo.parent.mkdir(parents=True)
    for nombre in ("application", "adapters", "infrastructure"):
        (tmp_path / "src" / nombre).mkdir()
    archivo.write_text(sentencia, encoding="utf-8")
    assert list(infracciones(archivo, tmp_path))


def test_guardia_permite_dependencia_relativa_del_dominio(tmp_path):
    archivo = tmp_path / "src/domain/services/ejemplo.py"
    archivo.parent.mkdir(parents=True)
    archivo.write_text("from ..entities import Informe\nfrom datetime import date", encoding="utf-8")
    assert not list(infracciones(archivo, tmp_path))
