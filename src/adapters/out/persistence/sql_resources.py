"""Consultas internas empaquetadas junto a los adaptadores de persistencia."""
from functools import cache
from importlib.resources import files


@cache
def consulta(adaptador: str, nombre: str) -> str:
    """Los nombres son constantes del adaptador; los valores siguen siendo parametros."""
    resource = files(__package__).joinpath("sql").joinpath(adaptador).joinpath(nombre + ".sql")
    return resource.read_text(encoding="utf-8").strip()
