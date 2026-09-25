import json

from src.domain.services.errores import DatosInvalidos


def validar_contenido(contenido: dict) -> None:
    if not isinstance(contenido, dict):
        raise DatosInvalidos("El contenido debe ser un objeto JSON")
    for seccion in ("antecedentes", "desarrollo", "conclusiones"):
        texto = contenido.get(seccion)
        if not isinstance(texto, str) or not texto.strip():
            raise DatosInvalidos(f"La sección {seccion} es obligatoria")
    try:
        json.dumps(contenido, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise DatosInvalidos("El contenido debe ser JSON válido") from error
