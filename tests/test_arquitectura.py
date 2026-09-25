import ast
import importlib
from pathlib import Path


def test_dominio_y_aplicacion_no_importan_infraestructura():
    prohibidos = ("src.adapters", "src.infrastructure", "fastapi", "pydantic",
                  "supabase", "ollama", "sklearn", "httpx", "requests")
    for capa in ("domain", "application"):
        for archivo in Path("src", capa).rglob("*.py"):
            arbol = ast.parse(archivo.read_text(encoding="utf-8"))
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.Import):
                    modulos = [a.name for a in nodo.names]
                elif isinstance(nodo, ast.ImportFrom):
                    modulos = [nodo.module or ""]
                else:
                    continue
                assert not any(m == p or m.startswith(p + ".") for m in modulos for p in prohibidos), archivo


def test_todos_los_modulos_se_importan_sin_servicios_externos():
    for archivo in Path("src").rglob("*.py"):
        importlib.import_module(".".join(archivo.with_suffix("").parts))
