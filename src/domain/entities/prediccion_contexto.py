from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.entities.solicitud import ahora
from src.domain.value_objects.estados import ResultadoValidacion


@dataclass
class NormativaPredicha:
    normativa_id: UUID
    confianza: float | None
    orden: int | None
    id: UUID = field(default_factory=uuid4)
    aceptada: bool | None = None


@dataclass
class PrediccionContexto:
    solicitud_id: UUID
    tipo_informe_predicho_id: UUID | None
    area_destino_predicha_id: UUID | None
    confianza_tipo: float | None
    confianza_area: float | None
    modelo: str
    id: UUID = field(default_factory=uuid4)
    version_modelo: str | None = None
    parametros: dict[str, Any] = field(default_factory=dict)
    resultado_validacion: ResultadoValidacion = ResultadoValidacion.PENDIENTE
    validado_por: UUID | None = None
    validado_at: datetime | None = None
    created_at: datetime = field(default_factory=ahora)
    normativas: list[NormativaPredicha] = field(default_factory=list)
