from typing import Annotated
from typing import Literal
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, File, Form, Query, Response, UploadFile
from pydantic import BaseModel, Field

from src.domain.services.errores import DatosInvalidos, ErrorServicio
from src.infrastructure.dependencies import Dependencias, Usuario
from ..schemas.error_response import RESPUESTAS_ERROR


router = APIRouter(prefix="/documentos", tags=["Documentos y RAG"], responses=RESPUESTAS_ERROR)


class DocumentoResponse(BaseModel):
    id: UUID
    titulo: str
    nombre_original: str
    tipo: str
    tamano: int
    sha256: str
    usuario_id: UUID
    procedencia: str
    ambito: str
    area_id: UUID | None
    estado: str
    error: str | None
    procesamiento: str | None
    fragmentos: int
    created_at: datetime
    updated_at: datetime


class FuenteResponse(BaseModel):
    documento_id: UUID
    fragmento_id: UUID
    titulo: str
    procedencia: str
    sha256: str
    tipo: str | None = None
    nombre_original: str | None = None
    texto: str
    localizacion: str
    inicio: int
    fin: int
    similitud: float = Field(description="1 menos distancia coseno; mayor es mejor")
    citas: list[dict] = Field(default_factory=list)


class RecuperacionResponse(BaseModel):
    estado: Literal["CORPUS_VACIO", "SIN_RESULTADOS", "RECUPERADO"]
    fuentes: list[FuenteResponse]
    procesamiento: str
    umbral_similitud: float | None = None


class FragmentoResponse(BaseModel):
    id: UUID
    documento_id: UUID
    texto: str
    localizacion: str
    inicio: int
    fin: int
    procesamiento: str


class ConfiguracionResponse(BaseModel):
    habilitado: bool
    max_bytes: int
    formatos: list[str]
    modelo_embeddings: str
    dimension: int


class ConsultaRag(BaseModel):
    consulta: str = Field(min_length=1, max_length=12000)


def servicio(deps):
    if deps.documentos is None:
        raise ErrorServicio("RAG_DESACTIVADO", "Gestión documental no activada; revise la guía PMV2")
    return deps.documentos


def representar(doc):
    return {k: (getattr(doc, k).isoformat() if k.endswith("_at") else getattr(doc, k))
            for k in DocumentoResponse.model_fields}


@router.get("/configuracion", response_model=ConfiguracionResponse, summary="Disponibilidad y límites de carga documental")
def configuracion(usuario: Usuario, deps: Dependencias):
    config = deps.rag_config
    return {"habilitado": deps.documentos is not None, "max_bytes": config.max_bytes,
            "formatos": config.formats, "modelo_embeddings": config.embedding_model,
            "dimension": config.embedding_dimension}


@router.get("", response_model=list[DocumentoResponse], summary="Listar solo documentos autorizados")
def listar(usuario: Usuario, deps: Dependencias, limite: Annotated[int, Query(ge=1, le=100)] = 100,
           offset: Annotated[int, Query(ge=0)] = 0):
    return [representar(d) for d in servicio(deps).listar(usuario, limite, offset)]


@router.post("", response_model=DocumentoResponse, status_code=201,
             summary="Incorporar un PDF con texto, DOCX o TXT autorizado",
             description="Multipart. Valida contenido antes de guardar; deduplica por propietario, ámbito, área y hash. "
                         "INSTITUCIONAL requiere administrador. No devuelve rutas privadas.")
def cargar(usuario: Usuario, deps: Dependencias, archivo: Annotated[UploadFile, File()],
           titulo: Annotated[str, Form(max_length=250)], procedencia: Annotated[str, Form(max_length=1000)],
           ambito: Annotated[str, Form()] = "PRIVADO"):
    gestor = servicio(deps)
    try:
        contenido = archivo.file.read(gestor.config.max_bytes + 1)
        if len(contenido) > gestor.config.max_bytes:
            raise DatosInvalidos("El archivo supera el límite configurado")
        return representar(gestor.cargar(usuario, archivo.filename, contenido, titulo, procedencia, ambito))
    finally:
        archivo.file.close()


@router.post("/recuperar", response_model=RecuperacionResponse, summary="Recuperar fragmentos autorizados; similitud coseno mayor es mejor")
def recuperar(request: ConsultaRag, usuario: Usuario, deps: Dependencias):
    return servicio(deps).recuperar(request.consulta, usuario)


@router.get("/{documento_id}", response_model=DocumentoResponse)
def obtener(documento_id: UUID, usuario: Usuario, deps: Dependencias):
    return representar(servicio(deps).obtener(documento_id, usuario))


@router.post("/{documento_id}/procesar", response_model=DocumentoResponse,
             summary="Extraer e indexar; reintentar fallos o reservas vencidas",
             description="Publicación atómica del índice por intento. Un documento ya indexado con la misma revisión no se duplica.")
def procesar(documento_id: UUID, usuario: Usuario, deps: Dependencias):
    return representar(servicio(deps).procesar(documento_id, usuario))


@router.get("/{documento_id}/fragmentos/{fragmento_id}", response_model=FragmentoResponse)
def fragmento(documento_id: UUID, fragmento_id: UUID, usuario: Usuario, deps: Dependencias):
    return servicio(deps).fragmento(documento_id, fragmento_id, usuario)


@router.get("/{documento_id}/original", response_class=Response, summary="Descargar original con autorización actual",
            responses={200: {"content": {"application/octet-stream": {}}}})
def original(documento_id: UUID, usuario: Usuario, deps: Dependencias):
    doc, contenido = servicio(deps).original(documento_id, usuario)
    return Response(contenido, media_type="application/octet-stream",
                    headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                             "Content-Disposition": f'attachment; filename="NAXJI-fuente-{doc.id}.{doc.tipo}"'})
