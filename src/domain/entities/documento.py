"""Documentos de referencia; no acreditan hechos del expediente."""
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.entities.solicitud import ahora
from src.domain.value_objects.estados import Rol


@dataclass
class Documento:
    titulo: str
    nombre_original: str
    tipo: str
    tamano: int
    sha256: str
    usuario_id: UUID
    procedencia: str
    ambito: str
    area_id: UUID | None
    id: UUID = field(default_factory=uuid4)
    ubicacion: str = ""
    estado: str = "SUBIENDO"
    error: str | None = None
    intento: UUID | None = None
    reserva_hasta: datetime | None = None
    procesamiento: str | None = None
    fragmentos: int = 0
    created_at: datetime = field(default_factory=ahora)
    updated_at: datetime = field(default_factory=ahora)


def puede_leer(documento, usuario):
    return bool(usuario.activo and usuario.roles and (
        Rol.ADMINISTRADOR in usuario.roles or documento.usuario_id == usuario.id
        or documento.ambito == "INSTITUCIONAL"
        or (documento.ambito == "AREA" and usuario.area_id is not None
            and documento.area_id == usuario.area_id)))
