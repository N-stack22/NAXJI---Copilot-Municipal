"""Smoke de imagen local sin red: usuario, PORT, salud, recursos y fallo cerrado."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from time import sleep
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def main():
    destino = ROOT / "docs/evidencias/cierre-seguridad-20261126/empaquetado/smoke-imagen"
    destino.mkdir(exist_ok=False)
    image = "naxji-cierre-seguridad:release"
    nombre = "naxji-smoke-" + uuid4().hex[:10]
    def run(args):
        return subprocess.run(["docker", *args], capture_output=True, text=True)
    meta = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "imagen": image, "red": "none",
            "puertos_publicados": [], "credenciales_externas": False,
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    r = run(["run", "-d", "--name", nombre, "--network", "none", "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=128m",
             "-e", "NAXJI_PERSISTENCE_MODE=memory", "-e", "NAXJI_AUTH_MODE=mock", "-e", "PORT=8088", image])
    assert r.returncode == 0, r.stderr
    container_id = r.stdout.strip()
    meta["contenedor_id"] = container_id
    try:
        for _ in range(45):
            probe = run(["exec", container_id, "python", "-c", "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8088/health',timeout=2).status==200"])
            if probe.returncode == 0:
                break
            sleep(1)
        assert probe.returncode == 0, probe.stderr
        r = run(["exec", container_id, "id", "-u"])
        meta["uid"] = r.stdout.strip()
        assert meta["uid"] == "10001"
        codigo = """import json,urllib.request,urllib.error
from importlib.resources import files
import src.adapters.out.persistence as persistence
r=urllib.request.urlopen('http://127.0.0.1:8088/health')
assert r.headers['X-Content-Type-Options']=='nosniff'
try: urllib.request.urlopen('http://127.0.0.1:8088/docs')
except urllib.error.HTTPError as e: assert e.code==404
else: raise AssertionError('Swagger debe estar desactivado')
resources=list(files(persistence).joinpath('sql').glob('*/*.sql'))
assert resources and all(p.read_text().strip() for p in resources)
from src.adapters.out.ai.sklearn_context_predictor import SklearnContextPredictor
SklearnContextPredictor()
from src.adapters.out.documents.exportador_pdf import ExportadorPdf
ExportadorPdf()
print(json.dumps({'health':200,'nosniff':True,'docs':404,'sql_recursos':len(resources),'predictor_cargado':True,'pdf_importado':True}))
"""
        r = run(["exec", container_id, "python", "-c", codigo])
        assert r.returncode == 0, r.stderr
        meta["checks"] = json.loads(r.stdout)
        inspeccion = json.loads(run(["inspect", container_id]).stdout)[0]
        meta["image_id"] = inspeccion["Image"]
        meta["read_only"] = inspeccion["HostConfig"]["ReadonlyRootfs"]
        assert meta["read_only"]
        (destino / "servidor.log").write_text(run(["logs", container_id]).stderr, encoding="utf-8")
    finally:
        assert run(["inspect", "--format", "{{.Name}}", container_id]).stdout.strip() == "/"+nombre
        meta["limpieza_exit"] = run(["rm", "-f", container_id]).returncode
    r = run(["run", "--rm", "--network", "none", image])
    (destino / "arranque-sin-config.log").write_text(r.stdout+r.stderr, encoding="utf-8")
    meta["arranque_sin_config_exit"] = r.returncode
    meta["fallo_cerrado_sin_config"] = r.returncode != 0 and "Faltan variables: NAXJI_DB_" in r.stderr
    assert meta["fallo_cerrado_sin_config"]
    (destino / "resultado.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
