from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.infrastructure.dependencies import Dependencias, Usuario
from src.infrastructure.diagnostico import preparacion
from src.application.use_cases.servicios_solicitud import autorizar
from src.domain.value_objects.estados import Rol
from src.domain.services.errores import NoAutorizado

router = APIRouter(tags=["Operación"])


@router.get("/ready")
def ready(usuario: Usuario, deps: Dependencias, request: Request):
    autorizar(usuario)
    if Rol.ADMINISTRADOR not in usuario.roles:
        raise NoAutorizado("Comprobación operativa reservada a administración")
    resultado = preparacion(request.app.state.settings, deps)
    return JSONResponse(resultado, status_code=200 if resultado["ready"] else 503,
                        headers={"Cache-Control": "no-store"})
