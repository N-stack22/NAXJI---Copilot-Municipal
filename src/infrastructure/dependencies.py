from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.domain.entities.usuario_actual import UsuarioActual
from src.infrastructure.configuration.container import Container


bearer = HTTPBearer(auto_error=False, description="DEMO: use demo-funcionario. No valida tokens de Supabase.")


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_current_user(request: Request, credentials: Annotated[
    HTTPAuthorizationCredentials | None, Depends(bearer),
]) -> UsuarioActual:
    usuario = None
    if request.app.state.settings.auth_mode == "mock" and credentials:
        usuario = request.app.state.usuarios_demo.get(credentials.credentials)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Autenticación requerida o token inválido",
                            headers={"WWW-Authenticate": "Bearer"})
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Perfil inactivo")
    return usuario


Usuario = Annotated[UsuarioActual, Depends(get_current_user)]
Dependencias = Annotated[Container, Depends(get_container)]
