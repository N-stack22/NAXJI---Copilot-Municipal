from pydantic import Field, JsonValue

from .base import RequestModel, Texto


class GenerarBorradorRequest(RequestModel):
    instrucciones: Texto = "Respetar los datos y la plantilla seleccionada."


class InformeRequest(RequestModel):
    contenido: dict[str, JsonValue]
    numero_version: int = Field(strict=True, ge=1, description="Versión que se editó; evita sobrescrituras concurrentes")
    titulo: Texto | None = None
