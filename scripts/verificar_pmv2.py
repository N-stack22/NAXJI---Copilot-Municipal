"""Registra checks sin leer secretos ni escribir en Supabase.

python scripts/verificar_pmv2.py --pg-port 55433 --ia-real
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pg-port", type=int)
    parser.add_argument("--ia-real", action="store_true")
    args = parser.parse_args()
    if args.ia_real and not args.pg_port:
        parser.error("--ia-real requiere --pg-port de un clúster exclusivo de pruebas")
    entorno = {k:v for k,v in os.environ.items() if not k.startswith("NAXJI_")}
    entorno.update(NAXJI_RUN_DB_TESTS="0", NAXJI_RUN_AUTH_TESTS="0", NAXJI_RUN_OLLAMA_TESTS="0", NAXJI_RUN_PMV2_AI_TESTS="0")
    entorno.update(NAXJI_PERSISTENCE_MODE="memory", NAXJI_AUTH_MODE="mock", NAXJI_RAG_ENABLED="false", NAXJI_PMV3_ENABLED="false")
    if args.pg_port:
        entorno["NAXJI_TEST_PG_PORT"] = str(args.pg_port)
    else:
        entorno.pop("NAXJI_TEST_PG_PORT", None)
    sello = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    destino = ROOT / "docs/evidencias/pmv2" / sello
    destino.mkdir(parents=True, exist_ok=False)
    print("Evidencia nueva: " + str(destino), flush=True)
    entorno["NAXJI_PMV2_EVIDENCE_DIR"] = str(destino)
    npm = "npm.cmd" if os.name == "nt" else "npm"
    comandos = [("pytest", [sys.executable, "-m", "pytest", "-q"]),
                ("frontend", [npm, "run", "test:frontend"]),
                ("lint", [npm, "run", "lint"]), ("build", [npm, "run", "build"]),
                ("diff-check", ["git", "diff", "--check"])]
    if args.ia_real:
        comandos.append(("pmv2-real", [sys.executable, "-m", "pytest", "-q", "tests/test_pmv2_postgres.py"]))
    resultados = []
    for nombre, comando in comandos:
        print("Ejecutando " + nombre, flush=True)
        individual = {**entorno, "NAXJI_RUN_PMV2_AI_TESTS": "1" if nombre == "pmv2-real" else "0"}
        inicio = datetime.now(timezone.utc)
        proceso = subprocess.run(comando, cwd=ROOT, env=individual, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (destino / (nombre + ".txt")).write_text((proceso.stdout + proceso.stderr).rstrip() + "\n", encoding="utf-8")
        resultados.append({"check": nombre, "comando": comando[1:] if nombre == "pytest" else comando,
                           "exit_code": proceso.returncode, "inicio_utc": inicio.isoformat(),
                           "segundos": (datetime.now(timezone.utc)-inicio).total_seconds(), "log": nombre + ".txt"})
        print(f"{nombre}: exit {proceso.returncode}", flush=True)
    rama = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    (destino / "checks.json").write_text(json.dumps({"rama": rama, "fecha_cliente": datetime.now(ZoneInfo("America/Lima")).date().isoformat(), "pg_aislado": bool(args.pg_port),
        "auth_storage": "Dobles; no validar como Supabase real", "resultados": resultados}, ensure_ascii=False, indent=2), encoding="utf-8")
    return int(any(r["exit_code"] for r in resultados))


if __name__ == "__main__":
    raise SystemExit(main())
