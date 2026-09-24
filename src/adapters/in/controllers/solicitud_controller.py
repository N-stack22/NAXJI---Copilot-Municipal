from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.domain.entities.solicitud import Solicitud
from src.application.use_cases.crear_solicitud import CrearSolicitud
from src.application.use_cases.obtener_solicitud import ObtenerSolicitud
from src.adapters.out.persistence.solicitud_repository_memory import (
    SolicitudRepositoryMemory,
)


router = APIRouter(
    prefix="/solicitudes",
    tags=["Solicitudes"]
)


repository = SolicitudRepositoryMemory()

crear_solicitud = CrearSolicitud(repository)
obtener_solicitud = ObtenerSolicitud(repository)


class SolicitudRequest(BaseModel):
    asunto: str
    descripcion: str


@router.post("/")
def crear(request: SolicitudRequest):

    solicitud = Solicitud(
        id=None,
        asunto=request.asunto,
        descripcion=request.descripcion
    )

    try:
        resultado = crear_solicitud.ejecutar(solicitud)
        return resultado

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/{solicitud_id}")
def obtener(solicitud_id: int):

    solicitud = obtener_solicitud.ejecutar(solicitud_id)

    if solicitud is None:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada"
        )

    return solicitud