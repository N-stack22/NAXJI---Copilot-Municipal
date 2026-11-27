"""Comprobaciones de lectura, sin migraciones ni generación, con errores sanitizados."""
import httpx
from src.adapters.out.persistence.estado_postgres import comprobar_postgres


def preparacion(settings, container):
    checks = {}
    if container.persistence_mode == "postgres":
        try:
            documentos, revisiones, vector = comprobar_postgres(container.uow.settings)
            checks["postgres"] = True
            if settings.rag.enabled:
                checks["pgvector_documentos"] = bool(documentos and vector)
            if settings.pmv3_enabled:
                checks["revision_migrada"] = bool(revisiones)
        except Exception:
            checks["postgres"] = False
    else:
        checks["memoria_temporal"] = True
    try:
        with httpx.Client(timeout=2, trust_env=False, follow_redirects=False) as client:
            respuesta = client.get(settings.ollama_base_url + "/api/tags")
            respuesta.raise_for_status()
            modelos = {m["name"] for m in respuesta.json()["models"]}
            checks["modelo_generacion"] = settings.ollama_model in modelos
            if settings.rag.enabled:
                checks["modelo_embeddings"] = settings.rag.embedding_model in modelos
    except Exception:
        checks["ollama"] = False
    if settings.rag.enabled:
        try:
            # El adaptador usa timeout acotado; solo se lee la configuración del bucket.
            almacen = container.documentos.almacen
            with httpx.Client(timeout=2, trust_env=False, follow_redirects=False,
                              headers={"apikey": almacen.clave, "Authorization": "Bearer " + almacen.clave}) as client:
                almacen._privado(client)
            checks["storage_privado"] = True
        except Exception:
            checks["storage_privado"] = False
    return {"ready": all(checks.values()), "comprobaciones": checks,
            "alcance": "Disponibilidad técnica de lectura; no certifica permisos efectivos ni aceptación institucional",
            "persistencia": container.persistence_mode, "rag": settings.rag.enabled, "revision": settings.pmv3_enabled}
