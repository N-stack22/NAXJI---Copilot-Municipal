"""ZAP oficial contra dos destinos FIJOS de una red Docker interna, nunca producción."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "ghcr.io/zaproxy/zaproxy@sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af"
NETWORK = "naxji-cierre-seguridad"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fase", choices=("antes", "despues"), required=True)
    parser.add_argument("--corrida", type=int, choices=range(1, 10), default=1)
    args = parser.parse_args()
    destino = ROOT / "docs/evidencias/cierre-seguridad-20261126/zap" / (args.fase + (f"-{args.corrida:02d}" if args.corrida > 1 else ""))
    destino.mkdir(parents=True, exist_ok=False)
    red = json.loads(subprocess.check_output(["docker", "network", "inspect", NETWORK]))[0]
    assert red["Internal"] is True, "El escáner solo puede usar una red sin salida externa"
    meta = {"inicio_utc": datetime.now(timezone.utc).isoformat(), "imagen": IMAGE,
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
            "red": NETWORK, "red_interna": True, "produccion": "No probada", "escaneos": []}
    planes = [
        ("frontend", "zap-baseline.py", ["-t", "http://naxji-api:8001/", "-m", "1", "-T", "3"], []),
        ("api-funcionario", "zap-api-scan.py", ["-t", "http://naxji-api:8000/openapi.json", "-f", "openapi", "-T", "3"],
         ["-e", "ZAP_AUTH_HEADER_VALUE=Bearer demo-funcionario", "-e", "ZAP_AUTH_HEADER_SITE=naxji-api"]),
    ]
    for nombre, script, opciones, entorno in planes:
        comando = ["docker", "run", "--rm", "--network", NETWORK, "--memory", "3g", "--cpus", "2",
                   "-e", "JAVA_OPTS=-Xmx1536m", *entorno, "-v", f"{destino}:/zap/wrk:rw", IMAGE,
                   script, *opciones, "-r", nombre+".html", "-J", nombre+".json",
                   "-z", "-config ascan.maxRuleDurationInMins=1 -config ascan.maxScanDurationInMins=5 -config ascan.threadPerHost=2"]
        inicio = datetime.now(timezone.utc)
        print("ZAP "+args.fase+" / "+nombre, flush=True)
        with (destino/(nombre+".log")).open("wb") as log:
            r = subprocess.run(comando, stdout=log, stderr=subprocess.STDOUT, timeout=900)
        registro = {"nombre": nombre, "comando": comando, "inicio_utc": inicio.isoformat(),
                    "fin_utc": datetime.now(timezone.utc).isoformat(), "exit_code": r.returncode}
        meta["escaneos"].append(registro)
        (destino/"ejecucion.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(nombre+": exit "+str(r.returncode), flush=True)
        if r.returncode not in (0, 1, 2):
            return r.returncode
    cobertura = subprocess.check_output(["docker", "exec", "naxji-cierre-seguridad-app", "python", "-c",
        "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/_laboratorio/cobertura').read().decode())"])
    (destino/"cobertura-http.json").write_bytes(cobertura)
    return 0


if __name__ == "__main__":
    sys.exit(main())
