from uuid import UUID

from fastapi import APIRouter

from src.infrastructure.dependencies import Dependencias, Usuario
from ..schemas.error_response import RESPUESTAS_ERROR
from ..schemas.informe_request import GenerarBorradorRequest
from ..schemas.informe_response import InformeResponse, representar_informe
from ..schemas.prediccion_request import ValidarPrediccionRequest
from ..schemas.prediccion_response import PrediccionResponse, representar_prediccion


router = APIRouter(prefix="/solicitudes", tags=["Contexto y borrador (MOCK)"], responses=RESPUESTAS_ERROR)


@router.post("/{solicitud_id}/predecir-contexto", response_model=PrediccionResponse,
             summary="Obtener una predicción ficticia; no ejecuta RF-IA-01")
def predecir(solicitud_id: UUID, usuario: Usuario, deps: Dependencias):
    prediccion = deps.predecir_contexto.ejecutar(solicitud_id, usuario)
    return representar_prediccion(prediccion, deps.catalogos)


@router.post("/{solicitud_id}/validar-prediccion", response_model=PrediccionResponse,
             summary="Aceptar, corregir o rechazar el contexto propuesto")
def validar(solicitud_id: UUID, request: ValidarPrediccionRequest, usuario: Usuario, deps: Dependencias):
    prediccion = deps.validar_prediccion.ejecutar(solicitud_id, usuario, **request.model_dump())
    return representar_prediccion(prediccion, deps.catalogos)


@router.post("/{solicitud_id}/generar-borrador", response_model=InformeResponse, status_code=201,
             summary="Generar y guardar un borrador MOCK; no llama a Ollama")
def generar(solicitud_id: UUID, request: GenerarBorradorRequest, usuario: Usuario, deps: Dependencias):
    informe = deps.generar_borrador.ejecutar(solicitud_id, usuario, request.instrucciones)
    return representar_informe(informe)
