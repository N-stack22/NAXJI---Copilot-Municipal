"""Validación OFFLINE de configuración de despliegue; solo muestra nombres, nunca valores."""
import json
import os
from urllib.parse import urlsplit


def verificar(values):
    errores = []
    required = ["NAXJI_DB_"+k for k in ("HOST", "PORT", "NAME", "USER", "PASSWORD", "SSLMODE")]
    required += ["NAXJI_SUPABASE_URL", "NAXJI_SUPABASE_PUBLISHABLE_KEY", "NAXJI_OLLAMA_BASE_URL",
                 "NAXJI_CORS_ORIGINS", "NAXJI_AUTH_ALLOWED_ORIGINS"]
    if values.get("NAXJI_RAG_ENABLED", "false").lower() == "true":
        required += ["NAXJI_STORAGE_SERVICE_KEY", "NAXJI_STORAGE_BUCKET"]
    for name in required:
        if not values.get(name) or values[name].startswith(("SU_", "<", "REEMPLAZAR")):
            errores.append(name+": falta configurar")
    for name, expected in (("NAXJI_PERSISTENCE_MODE", "postgres"), ("NAXJI_AUTH_MODE", "supabase"),
                           ("NAXJI_AUTH_COOKIE_SECURE", "true")):
        if values.get(name, "").lower() != expected:
            errores.append(name+": valor no apto para despliegue HTTPS")
    if values.get("NAXJI_DB_SSLMODE") not in {"require", "verify-ca", "verify-full"}:
        errores.append("NAXJI_DB_SSLMODE: TLS requerido")
    for name in ("NAXJI_CORS_ORIGINS", "NAXJI_AUTH_ALLOWED_ORIGINS"):
        for origin in filter(None, values.get(name, "").split(",")):
            u = urlsplit(origin.strip())
            if u.scheme != "https" or not u.hostname or "*" in origin or u.path not in ("", "/") or u.query or u.fragment:
                errores.append(name+": requiere orígenes HTTPS explícitos")
    ia = urlsplit(values.get("NAXJI_OLLAMA_BASE_URL", ""))
    if ia.hostname in {"localhost", "127.0.0.1", "::1"} or "ngrok" in (ia.hostname or ""):
        errores.append("NAXJI_OLLAMA_BASE_URL: requiere servicio privado estable")
    return sorted(set(errores))


if __name__ == "__main__":
    errores = verificar(os.environ)
    print(json.dumps({"offline": True, "conexion_a_servicios": False, "errores": errores,
                      "limite": "No verifica credenciales, disponibilidad, permisos ni migraciones"}, ensure_ascii=False))
    raise SystemExit(bool(errores))
