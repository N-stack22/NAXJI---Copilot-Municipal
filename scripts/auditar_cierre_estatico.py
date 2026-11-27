"""Inventario AST reproducible; no se presenta como salida de SciTools Understand."""
import argparse
import ast
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.test_arquitectura import dependencias, infracciones, nombre_modulo
from tests.test_sql_resources import adaptadores, consultas_referenciadas, sql_incrustado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    args.salida.mkdir(parents=True, exist_ok=False)
    archivos = sorted((ROOT / "src").rglob("*.py"))
    filas, errores, dinamicos = [], [], []
    for archivo in archivos:
        modulo = nombre_modulo(archivo)
        errores.extend(infracciones(archivo))
        for linea, target in dependencias(archivo):
            filas.append({"origen": modulo, "linea": linea, "destino": target})
        tree = ast.parse(archivo.read_text(encoding="utf-8-sig"))
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("import_module") and n.args and not isinstance(n.args[0], ast.Constant):
                dinamicos.append({"modulo": modulo, "linea": n.lineno, "expresion": ast.unparse(n.args[0])})
    with (args.salida / "dependencias.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["origen", "linea", "destino"])
        w.writeheader(); w.writerows(filas)
    persistencia = adaptadores()
    sql_embebido = [{"archivo": str(p.relative_to(ROOT)), "linea": linea} for p in persistencia for linea in sql_incrustado(p)]
    recursos = sorted({r for p in persistencia for r in consultas_referenciadas(p)})
    protegidos = ("src/domain", "src/application", "src/adapters/out/ai", "src/infrastructure/ai/models",
                  "src/adapters/out/persistence", "database", "src/adapters/in/web")
    diff = subprocess.check_output(["git", "diff", "7359a67", "--name-only", "--", *protegidos], cwd=ROOT, text=True).splitlines()
    reporte = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "herramienta": "AST Python propio, no Understand",
               "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "modulos": len(archivos), "por_capa": dict(Counter(nombre_modulo(p).split(".")[1] for p in archivos)),
               "dependencias_import": len(filas), "infracciones": errores, "imports_dinamicos_exteriores": dinamicos,
               "adaptadores_persistencia_descubiertos": len(persistencia), "sql_embebido": sql_embebido,
               "recursos_sql_referenciados": len(recursos), "recursos": recursos,
               "cambios_en_pilotos_predictor_rag_advertencias": diff,
               "limite": "AST/importaciones no sustituyen análisis de llamadas, complejidad o mantenibilidad de Understand"}
    (args.salida / "resultado.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: reporte[k] for k in ("modulos", "dependencias_import", "infracciones", "adaptadores_persistencia_descubiertos", "sql_embebido", "recursos_sql_referenciados", "cambios_en_pilotos_predictor_rag_advertencias")}, ensure_ascii=False))
    return int(bool(errores or sql_embebido or diff))


if __name__ == "__main__":
    raise SystemExit(main())
