import importlib
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.domain.services.errores import (
    ConflictoEstado, DatosInvalidos, ErrorDominio, ErrorGeneracion, NoAutorizado, NoEncontrado,
)
from src.infrastructure.auth.mock import usuarios_demo
from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings


logger = logging.getLogger(__name__)


def health():
    return {"status": "ok", "service": "NAXJI API"}


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(
        title="NAXJI API", version="1.0.0",
        description=("Backend PMV1 con persistencia en memoria e IA simulada. "
                     "En Authorize use demo-funcionario. Los datos desaparecen al reiniciar. "
                     "No conecta con Supabase, RF-IA-01 ni Ollama."),
    )
    app.state.settings = settings
    app.state.container = container or Container()
    app.state.usuarios_demo = usuarios_demo() if settings.auth_mode == "mock" else {}
    if settings.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                           allow_methods=["GET", "POST", "PUT"],
                           allow_headers=["Authorization", "Content-Type"])

    @app.exception_handler(ErrorDominio)
    async def error_dominio(request: Request, error: ErrorDominio):
        codigo = {DatosInvalidos: 400, NoAutorizado: 403, NoEncontrado: 404,
                  ConflictoEstado: 409, ErrorGeneracion: 500}.get(type(error), 400)
        mensaje = "No se pudo generar el borrador" if isinstance(error, ErrorGeneracion) else str(error)
        return JSONResponse(status_code=codigo, content={"detail": mensaje})

    @app.exception_handler(Exception)
    async def error_no_controlado(request: Request, error: Exception):
        # Única frontera global: registra el fallo sin exponer detalles internos por HTTP.
        logger.error("Error no controlado en %s", request.url.path,
                     exc_info=(type(error), error, error.__traceback__))
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})

    for nombre in ("solicitud", "catalogo", "ia", "informe", "usuario"):
        modulo = importlib.import_module(f"src.adapters.in.controllers.{nombre}_controller")
        app.include_router(modulo.router)
    app.add_api_route("/health", health, methods=["GET"], tags=["Estado"])
    return app


app = create_app()
