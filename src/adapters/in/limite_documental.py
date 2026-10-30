"""Límite ASGI previo al parser multipart, también sin Content-Length."""
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class LimiteDocumental:
    def __init__(self, app, max_bytes):
        self.app, self.max_bytes = app, max_bytes + 65536

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"].rstrip("/") != "/documentos":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        try:
            longitud = int(headers.get(b"content-length", b"0"))
        except ValueError:
            longitud = self.max_bytes + 1
        if longitud > self.max_bytes:
            respuesta = JSONResponse({"detail": "Carga superior al límite documental configurado", "codigo": "ARCHIVO_DEMASIADO_GRANDE"},
                                     status_code=413, headers={"Cache-Control": "no-store"})
            await respuesta(scope, receive, send)
            return
        total = 0
        async def limitado():
            nonlocal total
            mensaje = await receive()
            total += len(mensaje.get("body", b""))
            if total > self.max_bytes:
                raise HTTPException(status_code=413, detail="Carga superior al límite documental configurado")
            return mensaje
        await self.app(scope, limitado, send)
