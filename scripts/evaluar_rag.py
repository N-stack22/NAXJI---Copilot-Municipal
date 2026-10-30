"""Evaluación local reproducible. Solo corpus sintético; no lee credenciales/DB.

python scripts/evaluar_rag.py --output docs/evidencias/pmv2/recuperacion-real.json
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.adapters.out.ai.embeddings_ollama import EmbeddingsOllama  # noqa: E402


def evaluar(corpus, vectores_documentos, vectores_consultas, umbral, top_k):
    resultados = []
    for consulta, vector in zip(corpus["consultas"], vectores_consultas):
        ranking = sorted([{"id": d["id"], "similitud": sum(x*y for x, y in zip(vector, v))}
                          for d, v in zip(corpus["documentos"], vectores_documentos)], key=lambda r: -r["similitud"])
        seleccion = [r for r in ranking if r["similitud"] >= umbral][:top_k]
        relevantes = set(consulta["relevantes"])
        aciertos = len(relevantes.intersection(r["id"] for r in seleccion))
        resultados.append({"consulta_id": consulta["id"], "relevantes": sorted(relevantes), "ranking": ranking,
                           "seleccion": seleccion, "precision": aciertos/len(seleccion) if seleccion else 0,
                           "recall": aciertos/len(relevantes) if relevantes else None})
    positivas = [r for r in resultados if r["relevantes"]]
    negativas = [r for r in resultados if not r["relevantes"]]
    return {"umbral_similitud": umbral, "top_k": top_k,
            "hit_at_1": sum(bool(r["seleccion"] and r["seleccion"][0]["id"] in r["relevantes"]) for r in positivas)/len(positivas),
            "macro_recall_at_k": sum(r["recall"] for r in positivas)/len(positivas),
            "macro_precision_at_k": sum(r["precision"] for r in positivas)/len(positivas),
            "rechazo_negativas": sum(not r["seleccion"] for r in negativas)/len(negativas), "consultas": resultados}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--modelo", default="bge-m3:567m")
    args = parser.parse_args()
    archivo = ROOT / "tests/fixtures/pmv2_corpus.json"
    corpus = json.loads(archivo.read_text(encoding="utf-8"))
    adapter = EmbeddingsOllama(args.base_url, args.modelo)
    documentos = adapter.codificar([d["texto"] for d in corpus["documentos"]])
    consultas = adapter.codificar([q["texto"] for q in corpus["consultas"]])
    resultado = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "corpus": corpus["id"],
        "corpus_sha256": sha256(archivo.read_bytes()).hexdigest(), "modelo": adapter.modelo, "dimension": adapter.dimension,
        "tipo": "Embeddings reales; ranking coseno exhaustivo en Python, sin PostgreSQL ni LLM",
        "limite": "Calibración sobre el mismo corpus sintético pequeño; no estima calidad institucional ni precisión de citas.",
        "evaluaciones": [evaluar(corpus, documentos, consultas, u, k) for u in [0.4, 0.5, 0.55, 0.6, 0.65, 0.7] for k in [1, 3, 6]]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"corpus": corpus["id"], "resultados": [{k: v for k, v in r.items() if k != "consultas"}
                                                             for r in resultado["evaluaciones"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
