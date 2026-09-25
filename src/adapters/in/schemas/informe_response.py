from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from src.domain.entities.informe import Informe
from src.domain.value_objects.estados import EstadoInforme, OrigenVersion
from .base import ResponseModel


class InformeResponse(ResponseModel):
    informe_id: UUID
    solicitud_id: UUID
    plantilla_id: UUID
    titulo: str | None
    estado: EstadoInforme
    version_id: UUID
    numero_version: int
    contenido: dict[str, JsonValue]
    origen: OrigenVersion
    modelo_ia: str | None
    created_at: datetime
    updated_at: datetime


def representar_informe(informe: Informe) -> InformeResponse:
    version = max(informe.versiones, key=lambda v: v.numero_version)
    return InformeResponse(
        informe_id=informe.id, solicitud_id=informe.solicitud_id, plantilla_id=informe.plantilla_id,
        titulo=informe.titulo, estado=informe.estado, version_id=version.id,
        numero_version=version.numero_version, contenido=version.contenido,
        origen=version.origen, modelo_ia=version.modelo_ia,
        created_at=informe.created_at, updated_at=informe.updated_at,
    )
