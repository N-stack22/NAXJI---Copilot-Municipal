"""Objetivo desechable de ZAP. Nunca lee .env ni conecta servicios compartidos."""
import os
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.main import create_app
from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings
from src.infrastructure.configuration.rag import RagSettings
from src.infrastructure.auth.mock import usuarios_demo
from src.application.use_cases.documentos import GestionDocumentos
from src.adapters.out.documents.extractor import ExtractorArchivos
from src.adapters.out.ai.context_predictor_mock import ContextPredictorMock
from src.adapters.out.ai.generador_borrador_mock import GeneradorBorradorMock
from tests.pmv2_dobles import AlmacenMemoria, DocumentosMemoria, EmbeddingsPrueba
from src.application.ports.input.solicitud_use_case import DatosSolicitud
from src.domain.value_objects.estados import ResultadoValidacion

rag = RagSettings(enabled=True)
documentos = GestionDocumentos(DocumentosMemoria(), AlmacenMemoria(), ExtractorArchivos(), EmbeddingsPrueba(), rag)
config = Settings(pmv3_enabled=True, rag=rag)
deps = Container(config, predictor=ContextPredictorMock(), generador=GeneradorBorradorMock(), documentos=documentos)
autor = usuarios_demo()["demo-funcionario"]
s = deps.crear_solicitud.ejecutar(autor, DatosSolicitud("CASO FICTICIO: inspección de residuos en parque"))
p = deps.predecir_contexto.ejecutar(s.id, autor)
deps.validar_prediccion.ejecutar(s.id, autor, p.id, ResultadoValidacion.ACEPTADA)
plantilla = next(p for p in deps.plantillas.listar() if p.tipo_informe_id == deps.predicciones.ultima(s.id).tipo_informe_predicho_id)
deps.actualizar_solicitud.ejecutar(s.id, autor, {"plantilla_id": plantilla.id})
deps.guardar_valores.ejecutar(s.id, autor, {c.id: "Sin evidencias: caso ficticio ZAP" for c in plantilla.campos if c.obligatorio})
informe = deps.generar_borrador.ejecutar(s.id, autor)
documento = documentos.cargar(autor, "fuente-ficticia.txt", b"Fuente ficticia: residuos en parques. No acredita hechos.", "Fuente FICTICIA ZAP", "Prueba local autorizada", "PRIVADO")
documentos.procesar(documento.id, autor)
api = create_app(config, deps)
from collections import Counter
conteos = Counter()


@api.middleware("http")
async def medir_cobertura(request, call_next):
    response = await call_next(request)
    ruta = request.scope.get("route")
    conteos[(request.method, getattr(ruta, "path", "no_identificada"), response.status_code,
             request.headers.get("authorization") == "Bearer demo-funcionario")] += 1
    return response


@api.get("/_laboratorio/cobertura", include_in_schema=False)
def cobertura():
    return [{"metodo": k[0], "ruta": k[1], "status": k[2], "identidad_prueba": k[3], "peticiones": v}
            for k, v in sorted(conteos.items())]

esquema = api.openapi()
esquema["servers"] = [{"url": "http://naxji-api:8000"}]
# OpenAPI del laboratorio contiene valores válidos para recorrer recursos propios.
valores = {"solicitud_id": str(s.id), "informe_id": str(informe.id), "documento_id": str(documento.id), "numero_version": 1}
for rutas in esquema["paths"].values():
    for operacion in rutas.values():
        if not isinstance(operacion, dict):
            continue
        for parametro in operacion.get("parameters", []):
            if parametro.get("name") in valores:
                parametro["example"] = valores[parametro["name"]]
api.openapi_schema = esquema

from fastapi import FastAPI
frontend_app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
static = Path(os.environ.get("NAXJI_ZAP_DIST", "/frontend"))


@frontend_app.middleware("http")
async def cabeceras_frontend(request, call_next):
    response = await call_next(request)
    archivo = static / "_headers"
    # Emula solo el bloque /* del archivo de configuración estática de Cloudflare Pages.
    if archivo.is_file():
        for linea in archivo.read_text().splitlines():
            if linea.startswith("  ") and ":" in linea:
                nombre, valor = linea.strip().split(":", 1)
                response.headers[nombre] = valor.strip()
    return response


if static.is_dir():
    frontend_app.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")

    @frontend_app.get("/{ruta:path}")
    def frontend(ruta: str):
        archivo = static / ruta
        if ruta in {"favicon.svg", "robots.txt"} and archivo.is_file():
            return FileResponse(archivo)
        return FileResponse(static / "index.html")


if __name__ == "__main__":
    from threading import Thread
    import uvicorn
    Thread(target=uvicorn.run, args=(frontend_app,), kwargs={"host": "0.0.0.0", "port": 8001, "access_log": False}, daemon=True).start()
    uvicorn.run(api, host="0.0.0.0", port=8000, access_log=False)
