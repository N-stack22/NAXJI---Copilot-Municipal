from uuid import UUID

from fastapi import APIRouter

from src.infrastructure.dependencies import Dependencias, Usuario
from ..schemas.error_response import RESPUESTAS_ERROR
from ..schemas.informe_request import InformeRequest
from ..schemas.informe_response import InformeResponse, representar_informe


router = APIRouter(prefix="/informes", tags=["Informes"], responses=RESPUESTAS_ERROR)


@router.get("/{informe_id}", response_model=InformeResponse)
def obtener(informe_id: UUID, usuario: Usuario, deps: Dependencias):
    return representar_informe(deps.obtener_informe.ejecutar(informe_id, usuario))


@router.put("/{informe_id}", response_model=InformeResponse, summary="Guardar una nueva versión del borrador")
def actualizar(informe_id: UUID, request: InformeRequest, usuario: Usuario, deps: Dependencias):
    informe = deps.actualizar_borrador.ejecutar(informe_id, usuario, **request.model_dump())
    return representar_informe(informe)
