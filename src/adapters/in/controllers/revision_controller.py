from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import Field

from src.infrastructure.dependencies import Dependencias, Usuario
from ..schemas.base import RequestModel

router = APIRouter(tags=["Revisión e historial"])


class VersionRequest(RequestModel):
    numero_version: int = Field(ge=1, strict=True)


class EdicionRequest(VersionRequest):
    contenido: dict[str, str]


class DecisionRequest(VersionRequest):
    decision: Literal["APROBADO", "RECHAZADO"]
    motivo: str = Field(min_length=1, max_length=4000)
    comprobaciones: dict[str, str] = Field(default_factory=dict, max_length=100)


def servicio(deps):
    if deps.revision is None:
        raise HTTPException(503, "La revisión e historial requieren activación y migración PMV3 en el servidor")
    return deps.revision


@router.get("/revision/config")
def configuracion(usuario: Usuario, deps: Dependencias):
    return {"enabled": deps.revision is not None}


@router.get("/revision/informes")
def listar(usuario: Usuario, deps: Dependencias, limite: Annotated[int, Query(ge=1, le=100)] = 25,
           desplazamiento: Annotated[int, Query(ge=0)] = 0):
    return servicio(deps).listar(usuario, limite, desplazamiento)


@router.get("/revision/informes/{informe_id}")
def historial(informe_id: UUID, usuario: Usuario, deps: Dependencias):
    return servicio(deps).historial(informe_id, usuario)


@router.post("/revision/informes/{informe_id}/enviar")
def enviar(informe_id: UUID, request: VersionRequest, usuario: Usuario, deps: Dependencias):
    return servicio(deps).enviar(informe_id, usuario, request.numero_version)


@router.post("/revision/informes/{informe_id}/editar")
def editar(informe_id: UUID, request: EdicionRequest, usuario: Usuario, deps: Dependencias):
    return servicio(deps).editar(informe_id, usuario, request.numero_version, request.contenido)


@router.post("/revision/informes/{informe_id}/decidir")
def decidir(informe_id: UUID, request: DecisionRequest, usuario: Usuario, deps: Dependencias):
    return servicio(deps).decidir(informe_id, usuario, **request.model_dump())


@router.get("/revision/informes/{informe_id}/versiones/{numero_version}/exportar")
def exportar(informe_id: UUID, numero_version: int, usuario: Usuario, deps: Dependencias,
             formato: Literal["docx", "pdf"] = "docx"):
    contenido = servicio(deps).exportar(informe_id, numero_version, usuario, formato)
    media = "application/pdf" if formato == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return Response(contenido, media_type=media, headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
        "Content-Disposition": f'attachment; filename="NAXJI-{informe_id}-v{numero_version}.{formato}"'})


@router.get("/auditoria")
def auditoria(usuario: Usuario, deps: Dependencias, limite: Annotated[int, Query(ge=1, le=100)] = 50,
              desplazamiento: Annotated[int, Query(ge=0)] = 0, informe_id: UUID | None = None):
    return servicio(deps).auditoria(usuario, limite, desplazamiento, informe_id)
