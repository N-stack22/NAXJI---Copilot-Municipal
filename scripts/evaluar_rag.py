"""Evaluación local reproducible. Solo corpus sintético; no lee credenciales/DB.

python scripts/evaluar_rag.py --output docs/evidencias/pmv2/recuperacion-real.json
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from math import isfinite
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.adapters.out.ai.embeddings_ollama import EmbeddingsOllama  # noqa: E402


def evaluar(corpus, vectores_documentos, vectores_consultas, umbral, top_k):
    documentos, consultas = corpus["documentos"], corpus["consultas"]
    ids = [d["id"] for d in documentos]
    qids = [q["id"] for q in consultas]
    if (not documentos or not consultas or len(set(ids)) != len(ids) or len(set(qids)) != len(qids)
            or len(vectores_documentos) != len(documentos) or len(vectores_consultas) != len(consultas)
            or type(top_k) is not int or top_k < 1 or not isfinite(umbral) or not -1 <= umbral <= 1):
        raise ValueError("Corpus, vectores, umbral o top_k incompatibles")
    dimensiones = {len(v) for v in vectores_documentos + vectores_consultas}
    if len(dimensiones) != 1 or 0 in dimensiones or any(not isfinite(x) for v in vectores_documentos + vectores_consultas for x in v):
        raise ValueError("Vectores no finitos o de dimensiones incompatibles")
    if any(set(q["relevantes"]) - set(ids) for q in consultas):
        raise ValueError("Ground truth referencia documentos inexistentes")
    resultados = []
    for consulta, vector in zip(corpus["consultas"], vectores_consultas):
        ranking = sorted([{"id": d["id"], "similitud": sum(x*y for x, y in zip(vector, v))}
                          for d, v in zip(corpus["documentos"], vectores_documentos)], key=lambda r: -r["similitud"])
        seleccion = [r for r in ranking if r["similitud"] >= umbral][:top_k]
        relevantes = set(consulta["relevantes"])
        aciertos = len(relevantes.intersection(r["id"] for r in seleccion))
        resultados.append({"consulta_id": consulta["id"], "relevantes": sorted(relevantes), "ranking": ranking,
                           "seleccion": seleccion, "precision": aciertos/len(seleccion) if seleccion else 0,
                           "recall": aciertos/len(relevantes) if relevantes else None,
                           "reciprocal_rank": next((1/(n+1) for n,r in enumerate(seleccion) if r["id"] in relevantes), 0)})
    positivas = [r for r in resultados if r["relevantes"]]
    negativas = [r for r in resultados if not r["relevantes"]]
    return {"umbral_similitud": umbral, "top_k": top_k,
            "positivas": len(positivas), "negativas": len(negativas),
            "hit_at_1": sum(bool(r["seleccion"] and r["seleccion"][0]["id"] in r["relevantes"]) for r in positivas)/len(positivas) if positivas else None,
            "hit_at_k": sum(any(r["id"] in q["relevantes"] for r in q["seleccion"]) for q in positivas)/len(positivas) if positivas else None,
            "mrr_at_k": sum(r["reciprocal_rank"] for r in positivas)/len(positivas) if positivas else None,
            "macro_recall_at_k": sum(r["recall"] for r in positivas)/len(positivas) if positivas else None,
            "macro_precision_at_k": sum(r["precision"] for r in positivas)/len(positivas) if positivas else None,
            "rechazo_negativas": sum(not r["seleccion"] for r in negativas)/len(negativas) if negativas else None, "consultas": resultados}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--modelo", default="bge-m3:567m")
    parser.add_argument("--corpus", type=Path, default=ROOT / "tests/fixtures/pmv2_corpus.json")
    args = parser.parse_args()
    archivo = args.corpus
    corpus = json.loads(archivo.read_text(encoding="utf-8"))
    adapter = EmbeddingsOllama(args.base_url, args.modelo)
    inicio = perf_counter()
    documentos = adapter.codificar([d["texto"] for d in corpus["documentos"]])
    tiempo_documentos = perf_counter()-inicio
    inicio = perf_counter()
    consultas = adapter.codificar([q["texto"] for q in corpus["consultas"]])
    tiempo_consultas = perf_counter()-inicio
    resultado = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "corpus": corpus["id"],
        "corpus_sha256": sha256(archivo.read_bytes()).hexdigest(), "modelo": adapter.modelo, "dimension": adapter.dimension,
        "tipo": "Embeddings reales; ranking coseno exhaustivo en Python, sin PostgreSQL ni LLM",
        "tiempos_lotes_s": {"documentos": tiempo_documentos, "consultas": tiempo_consultas},
        "limite": "El corpus predeterminado es sintético pequeño; no estima calidad institucional ni precisión de citas. Ground truth no equivale a revisión jurídica.",
        "evaluaciones": [evaluar(corpus, documentos, consultas, u, k) for u in [0.4, 0.5, 0.55, 0.6, 0.65, 0.7] for k in [1, 3, 6]]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as salida:
        salida.write(json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False))
    print(json.dumps({"corpus": corpus["id"], "resultados": [{k: v for k, v in r.items() if k != "consultas"}
                                                             for r in resultado["evaluaciones"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
