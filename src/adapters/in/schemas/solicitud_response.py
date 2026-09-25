from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from src.domain.value_objects.estado_solicitud import EstadoSolicitud
from .base import ResponseModel


class ValorResponse(ResponseModel):
    id: UUID
    solicitud_id: UUID
    campo_plantilla_id: UUID
    valor: JsonValue
    created_at: datetime
    updated_at: datetime


class SolicitudResponse(ResponseModel):
    id: UUID
    usuario_id: UUID
    asunto: str
    tipo_informe_id: UUID | None
    plantilla_id: UUID | None
    area_origen_id: UUID | None
    area_destino_id: UUID | None
    estado: EstadoSolicitud
    valores: list[ValorResponse]
    created_at: datetime
    updated_at: datetime
