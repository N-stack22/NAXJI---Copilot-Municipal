from uuid import UUID

from fastapi import APIRouter

from src.domain.value_objects.estados import Rol
from src.infrastructure.dependencies import Usuario
from ..schemas.base import ResponseModel
from ..schemas.error_response import RESPUESTAS_ERROR


class UsuarioResponse(ResponseModel):
    id: UUID
    roles: frozenset[Rol]
    area_id: UUID | None
    activo: bool


router = APIRouter(tags=["Usuario de prueba"], responses=RESPUESTAS_ERROR)


@router.get("/auth/me", response_model=UsuarioResponse)
def usuario_actual(usuario: Usuario):
    return usuario
