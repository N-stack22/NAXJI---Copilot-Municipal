from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects.estado_solicitud import EstadoSolicitud


def ahora() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class SolicitudValor:
    solicitud_id: UUID
    campo_plantilla_id: UUID
    valor: Any
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=ahora)
    updated_at: datetime = field(default_factory=ahora)


@dataclass
class Solicitud:
    usuario_id: UUID
    asunto: str
    id: UUID = field(default_factory=uuid4)
    tipo_informe_id: UUID | None = None
    plantilla_id: UUID | None = None
    area_origen_id: UUID | None = None
    area_destino_id: UUID | None = None
    estado: EstadoSolicitud = EstadoSolicitud.BORRADOR
    valores: list[SolicitudValor] = field(default_factory=list)
    created_at: datetime = field(default_factory=ahora)
    updated_at: datetime = field(default_factory=ahora)
