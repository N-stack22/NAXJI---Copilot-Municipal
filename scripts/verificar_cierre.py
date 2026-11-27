"""Registra checks actuales en un directorio NUEVO; no escribe Supabase compartido."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.evidencia_cierre import huella_fuentes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pg-port", type=int, required=True)
    parser.add_argument("--ia-real", action="store_true")
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    destino = args.salida.resolve()
    if not destino.is_relative_to(ROOT/"docs/evidencias"):
        parser.error("Conserve la evidencia en docs/evidencias del repositorio")
    destino.mkdir(parents=True, exist_ok=False)
    entorno = {k:v for k,v in os.environ.items() if not k.startswith("NAXJI_")}
    entorno.update(NAXJI_RUN_DB_TESTS="0", NAXJI_RUN_AUTH_TESTS="0", NAXJI_RUN_OLLAMA_TESTS="1" if args.ia_real else "0",
                   NAXJI_RUN_PMV2_AI_TESTS="1" if args.ia_real else "0", NAXJI_TEST_PG_PORT=str(args.pg_port),
                   NAXJI_PERSISTENCE_MODE="memory", NAXJI_AUTH_MODE="mock", NAXJI_RAG_ENABLED="false",
                   NAXJI_PMV3_ENABLED="false", PYTHONIOENCODING="utf-8")
    for nombre in ("PMV2", "PILOTO", "CONTENIDO", "INSPECCION", "MDT"):
        carpeta = destino/nombre.lower(); carpeta.mkdir()
        entorno[f"NAXJI_{nombre}_EVIDENCE_DIR"] = str(carpeta)
    npm = "npm.cmd" if os.name == "nt" else "npm"
    comandos = [("pytest", [sys.executable, "-m", "pytest", "-q", "-ra", "--basetemp", str(destino/"temporales")]),
                ("frontend", [npm,"run","test:frontend"]), ("lint",[npm,"run","lint"]),
                ("build",[npm,"run","build"]), ("diff-check",["git","diff","--check"])]
    informe = {"inicio_utc":datetime.now(timezone.utc).isoformat(),"commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
               "fuentes_manifest_sha256":huella_fuentes(destino),"postgres":"loopback aislado; bases aleatorias de fixtures",
               "ollama_real":args.ia_real,"supabase_compartido":"no conectado","checks":[]}
    for nombre, comando in comandos:
        print("Ejecutando "+nombre,flush=True)
        inicio = datetime.now(timezone.utc)
        r = subprocess.run(comando,cwd=ROOT,env=entorno,capture_output=True)
        (destino/(nombre+".txt")).write_bytes(r.stdout+r.stderr)
        informe["checks"].append({"check":nombre,"comando":comando,"inicio_utc":inicio.isoformat(),
                                 "duracion_s":(datetime.now(timezone.utc)-inicio).total_seconds(),"exit_code":r.returncode})
        informe["fin_utc"] = datetime.now(timezone.utc).isoformat()
        (destino/"checks.json").write_text(json.dumps(informe,ensure_ascii=False,indent=2),encoding="utf-8")
        print(nombre+": exit "+str(r.returncode),flush=True)
    return int(any(r["exit_code"] for r in informe["checks"]))


if __name__ == "__main__":
    raise SystemExit(main())
