from uuid import UUID

from src.domain.value_objects.estados import ResultadoValidacion
from .base import RequestModel


class ValidarPrediccionRequest(RequestModel):
    prediccion_id: UUID
    resultado: ResultadoValidacion
    tipo_informe_id: UUID | None = None
    area_destino_id: UUID | None = None
    normativa_ids: list[UUID] | None = None
