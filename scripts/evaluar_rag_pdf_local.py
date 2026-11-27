"""Recuperación real sobre extracto PDF autorizado, PG desechable y bge-m3 local.

Auth y Storage son dobles. No hay generación ni evaluación jurídica automática.
Las referencias esperadas son páginas físicas del PDF original, etiquetadas por
quien prepara el JSON de casos; no se presentan como evaluación institucional.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pypdf import PdfReader, PdfWriter
from src.adapters.out.ai.embeddings_ollama import EmbeddingsOllama
from tests.entorno_cierre import entorno_aislado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf",type=Path,required=True)
    parser.add_argument("--desde",type=int,required=True)
    parser.add_argument("--hasta",type=int,required=True)
    parser.add_argument("--casos",type=Path,required=True)
    parser.add_argument("--pg-port",type=int,required=True)
    parser.add_argument("--salida",type=Path,required=True)
    args=parser.parse_args()
    if args.salida.exists():parser.error("La evidencia debe ser nueva")
    pdf=PdfReader(args.pdf)
    if not 1 <= args.desde <= args.hasta <= len(pdf.pages):parser.error("Rango de páginas inválido")
    casos=json.loads(args.casos.read_text(encoding="utf-8"))
    if (not casos.get("autor_ground_truth") or not casos.get("consultas")
            or any(set(q["paginas_relevantes"])-set(range(args.desde,args.hasta+1)) for q in casos["consultas"])):
        parser.error("Identifique el etiquetado y use páginas del extracto")
    writer=PdfWriter()
    for pagina in range(args.desde-1,args.hasta):writer.add_page(pdf.pages[pagina])
    contenido=BytesIO();writer.write(contenido)
    resultados=[]
    with entorno_aislado(args.pg_port) as entorno:
        gestor=entorno.deps.documentos;autor=entorno.usuarios["autor"]
        gestor.embeddings=EmbeddingsOllama("http://127.0.0.1:11434","bge-m3:567m")
        gestor.procesamiento="eval-pdf-autorizado:bge-m3:567m:1024:1"
        doc=gestor.cargar(autor,"extracto-autorizado.pdf",contenido.getvalue(),"Extracto documental autorizado", "Extracto explícito para laboratorio; no acredita vigencia normativa ni hechos del caso", "PRIVADO")
        inicio=perf_counter();doc=gestor.procesar(doc.id,autor);tiempo_indice=perf_counter()-inicio
        for q in casos["consultas"]:
            inicio=perf_counter();r=gestor.recuperar(q["consulta"],autor);duracion=perf_counter()-inicio
            paginas=[int(f["localizacion"].rsplit(" ",1)[-1])+args.desde-1 for f in r["fuentes"]]
            relevantes=set(q["paginas_relevantes"])
            resultados.append({"id":q["id"],"consulta":q["consulta"],"paginas_relevantes":sorted(relevantes),
                "paginas_recuperadas":paginas,"similitudes":[f["similitud"] for f in r["fuentes"]],"estado":r["estado"],"segundos":duracion,
                "hit_at_1":bool(paginas and paginas[0] in relevantes) if relevantes else None,
                "hit_at_k":bool(set(paginas)&relevantes) if relevantes else None,
                "recall_paginas":len(set(paginas)&relevantes)/len(relevantes) if relevantes else None})
        sin_acceso=gestor.recuperar(casos["consultas"][0]["consulta"],entorno.usuarios["otro"])
        assert sin_acceso["estado"] == "CORPUS_VACIO" and not sin_acceso["fuentes"]
        positivas=[r for r in resultados if r["paginas_relevantes"]];negativas=[r for r in resultados if not r["paginas_relevantes"]]
        reporte={"fecha_utc":datetime.now(timezone.utc).isoformat(),"pdf_nombre":args.pdf.name,"pdf_sha256":sha256(args.pdf.read_bytes()).hexdigest(),
            "paginas_fisicas_originales":[args.desde,args.hasta],"casos_sha256":sha256(args.casos.read_bytes()).hexdigest(),
            "script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),"ground_truth_declarado":casos["autor_ground_truth"],
            "tipo":"PDF real local; PostgreSQL/pgvector y bge-m3 reales; Auth/Storage dobles; sin LLM",
            "fragmentos_indexados":doc.fragmentos,"tiempo_indexacion_s":tiempo_indice,"modelo":"bge-m3:567m","dimension":1024,
            "umbral":gestor.config.threshold,"top_k":gestor.config.top_k,"resultados":resultados,"permiso_ajeno_sin_resultados":True,
            "metricas":{"positivas":len(positivas),"negativas":len(negativas),"hit_at_1":sum(r["hit_at_1"] for r in positivas)/len(positivas) if positivas else None,
                        "hit_at_k":sum(r["hit_at_k"] for r in positivas)/len(positivas) if positivas else None,
                        "rechazo_negativas":sum(not r["paginas_recuperadas"] for r in negativas)/len(negativas) if negativas else None},
            "limites":"Muestra pequeña de un extracto, etiquetado técnico asistido y relevancia por página; no pertinencia semántica por afirmación, vigencia jurídica, representatividad ni revisión humana institucional"}
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    with args.salida.open("x",encoding="utf-8") as f:json.dump(reporte,f,ensure_ascii=False,indent=2)
    print(json.dumps(reporte["metricas"]))


if __name__ == "__main__":main()
