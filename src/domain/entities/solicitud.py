from dataclasses import dataclass
from typing import Optional


@dataclass
class Solicitud:
    id: Optional[int]
    asunto: str
    descripcion: str
    estado: str = "PENDIENTE"