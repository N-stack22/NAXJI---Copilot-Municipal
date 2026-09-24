import importlib

from fastapi import FastAPI


controller_module = importlib.import_module(
    "src.adapters.in.controllers.solicitud_controller"
)

solicitud_router = controller_module.router


app = FastAPI(
    title="NAXJI API",
    description="Back-End del sistema NAXJI",
    version="1.0.0"
)

app.include_router(solicitud_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "NAXJI API"
    }