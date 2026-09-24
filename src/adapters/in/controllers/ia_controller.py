from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.application.use_cases.generar_borrador import GenerarBorrador
from src.adapters.out.ai.ollama_adapter import OllamaAdapter


router = APIRouter(
    prefix="/ia",
    tags=["Inteligencia Artificial"]
)


llm = OllamaAdapter()
generar_borrador = GenerarBorrador(llm)


class GenerarBorradorRequest(BaseModel):
    asunto: str
    descripcion: str


@router.post("/generar-borrador")
def generar(request: GenerarBorradorRequest):

    try:
        resultado = generar_borrador.ejecutar(
            asunto=request.asunto,
            descripcion=request.descripcion
        )

        return {
            "status": "ok",
            "borrador": resultado
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el borrador: {str(error)}"
        )