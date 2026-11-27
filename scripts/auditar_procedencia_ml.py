"""Contrasta CSV/notebook locales con artefactos existentes. No publica datos ni guarda modelos.

Reconstruye la partición descrita por el notebook mejorado (70/15/15, semilla 42,
estratificación normativa). Ajusta clones únicamente en memoria para contrastar
vocabulario/IDF/coeficientes; nunca reemplaza ni reentrena el predictor de producción.
La coincidencia matemática no certifica cadena de custodia ni revisión de etiquetas.
"""
import argparse
import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from sklearn.base import clone
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import f1_score
from src.adapters.out.ai.sklearn_context_predictor import SklearnContextPredictor
from src.adapters.out.ai.integridad_modelos import verificar_artefactos
from scripts.evaluar_predictor import evaluar


def leer_csv(archivo):
    with archivo.open(encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        if set(lector.fieldnames or []) != {"sumilla", "tipo_informe", "normativas", "area_destino"}:
            raise ValueError("Columnas CSV incompatibles")
        filas = [{k: (v or "").strip() for k,v in r.items()} for r in lector]
    if not filas or any(not all(r.values()) for r in filas):
        raise ValueError("CSV vacío o con campos incompletos")
    return filas


def datos_evaluacion(filas, indices, fuente, particion):
    return {"metadata": {"fuente":fuente,"etiquetado":"Etiquetas del CSV local; autoría/revisión independiente no acreditadas",
                         "particion":particion,"independiente_entrenamiento":False},
            "casos":[{"id":f"fila-{i+2}", "asunto":filas[i]["sumilla"], "tipo_informe":filas[i]["tipo_informe"],
                      "area_destino":filas[i]["area_destino"], "temas_normativos":[s.strip() for s in filas[i]["normativas"].split("|") if s.strip()]} for i in indices]}


def sin_textos(resultado):
    tiempos = [p["inferencia_ms"] for p in resultado["predicciones"]]
    resultado = {k:v for k,v in resultado.items() if k != "predicciones"}
    resultado["latencia_inferencia_ms"] = dict(zip(["p50","p95","p99"],map(float,np.percentile(tiempos,[50,95,99]))))
    return resultado


def comparar_features(a, b):
    return {nombre: {"vocabulario_igual":va.vocabulary_ == vb.vocabulary_,
                     "idf_igual":bool(np.array_equal(va.idf_,vb.idf_))}
            for (nombre,va),(_,vb) in zip(a.transformer_list,b.transformer_list,strict=True)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv",required=True,type=Path)
    parser.add_argument("--notebook",required=True,type=Path)
    parser.add_argument("--csv-adicional",type=Path)
    parser.add_argument("--salida",required=True,type=Path)
    args = parser.parse_args()
    if args.salida.exists():
        parser.error("La evidencia debe ser un archivo nuevo")
    filas = leer_csv(args.csv)
    notebook = json.loads(args.notebook.read_text(encoding="utf-8"))
    codigo = "\n".join("".join(c.get("source",[])) for c in notebook["cells"] if c["cell_type"] == "code")
    if not all(s in codigo for s in ("test_size=0.30", "test_size=0.50", "random_state=42", 'stratify=df["normativas"]', "LogisticRegression")):
        parser.error("El notebook no describe la partición esperada; revisar manualmente, sin ejecutarlo")
    modelo = SklearnContextPredictor()
    indices = np.arange(len(filas))
    etiquetas = np.array([f["normativas"] for f in filas])
    train, temporal = train_test_split(indices,test_size=.30,random_state=42,stratify=etiquetas)
    val, test = train_test_split(temporal,test_size=.50,random_state=42,stratify=etiquetas[temporal])
    textos = np.array([f["sumilla"] for f in filas])
    tipos = np.array([f["tipo_informe"] for f in filas]); areas=np.array([f["area_destino"] for f in filas])
    tipo_clon = clone(modelo.modelo_tipo).fit(textos[train],tipos[train])
    area_clon = clone(modelo.modelo_area).fit(textos[train],areas[train])
    features_clon = clone(modelo.features_norm).fit(textos[train])
    mlb = MultiLabelBinarizer().fit([[s.strip() for s in f["normativas"].split("|")] for f in filas])
    y = mlb.transform([[s.strip() for s in f["normativas"].split("|")] for f in filas])
    normas_clon = clone(modelo.modelo_normas).fit(features_clon.transform(textos[train]),y[train])
    comparacion = {"tipo_features":comparar_features(modelo.modelo_tipo.steps[0][1],tipo_clon.steps[0][1]),
                  "area_features":comparar_features(modelo.modelo_area.steps[0][1],area_clon.steps[0][1]),
                  "normas_features":comparar_features(modelo.features_norm,features_clon),
                  "etiquetas_normativas_iguales":list(mlb.classes_) == list(modelo.mlb.classes_)}
    for nombre,original,replay in (("tipo",modelo.modelo_tipo.steps[-1][1],tipo_clon.steps[-1][1]),("area",modelo.modelo_area.steps[-1][1],area_clon.steps[-1][1])):
        comparacion[nombre+"_coeficientes_max_diferencia"] = float(np.max(np.abs(original.coef_-replay.coef_)))
        comparacion[nombre+"_predicciones_test_iguales"] = bool(np.array_equal(original.predict((modelo.modelo_tipo if nombre=="tipo" else modelo.modelo_area).steps[0][1].transform(textos[test])),replay.predict((tipo_clon if nombre=="tipo" else area_clon).steps[0][1].transform(textos[test]))))
    comparacion["normas_coeficientes_max_diferencia"] = float(max(np.max(np.abs(a.coef_-b.coef_)) for a,b in zip(modelo.modelo_normas.estimators_,normas_clon.estimators_,strict=True)))
    prob_val = normas_clon.predict_proba(features_clon.transform(textos[val]))
    umbrales = [{"umbral":u,"f1_micro_validacion":float(f1_score(y[val],prob_val >= u,average="micro",zero_division=0))}
                for u in (.20,.25,.30,.35,.40,.45,.50,.55,.60)]
    mejor_umbral = max(umbrales,key=lambda r:r["f1_micro_validacion"])["umbral"]
    pares_duplicados = len(textos)-len(set(t.casefold().strip() for t in textos))
    similitudes = cosine_similarity(modelo.features_norm.transform(textos[test]),modelo.features_norm.transform(textos[train]))
    informe = {"fecha_utc":datetime.now(timezone.utc).isoformat(), "csv_nombre":args.csv.name,
        "csv_sha256":sha256(args.csv.read_bytes()).hexdigest(), "notebook_nombre":args.notebook.name,
        "notebook_sha256":sha256(args.notebook.read_bytes()).hexdigest(), "filas":len(filas),
        "particiones_filas_csv_base1_con_cabecera":{"train":[int(i)+2 for i in train],"validacion":[int(i)+2 for i in val],"test":[int(i)+2 for i in test]},
        "algoritmos":modelo.algoritmos,"comparacion_clones_en_memoria":comparacion,
        "umbrales_replay_validacion":umbrales,"mejor_umbral_replay":mejor_umbral,"umbral_artefacto":modelo.umbral_normas,
        "f1_macro_tipo_tres_clases_poc":float(f1_score(tipos[test],modelo.modelo_tipo.predict(textos[test]),average="macro",zero_division=0)),
        "duplicados_textuales_normalizados":pares_duplicados,
        "similitud_test_train":{"representacion":"TF-IDF word+char del artefacto existente; coseno máximo por caso test",
                                "maximo":float(similitudes.max()),"mediana_maximos":float(np.median(similitudes.max(axis=1)))},
        "evaluacion_test_artefactos_existentes":sin_textos(evaluar(datos_evaluacion(filas,list(map(int,test)),args.csv.name,"test reconstruido del notebook; sin garantía externa"),modelo,medir=True)),
        "limitaciones":["Datos sintéticos; no son un corpus institucional independiente",
                        "No se ejecutó código del notebook ni se escribieron modelos",
                        "La concordancia de artefactos con un replay no certifica autoría, cadena de custodia o aprobación de etiquetas",
                        "Se publican agregados e índices; no se copian CSV/notebooks originales ni textos de casos"]}
    if args.csv_adicional:
        otras = leer_csv(args.csv_adicional)
        solapadas = sum(f["sumilla"].casefold().strip() in {t.casefold().strip() for t in textos} for f in otras)
        informe["csv_adicional"] = {"nombre":args.csv_adicional.name,"sha256":sha256(args.csv_adicional.read_bytes()).hexdigest(),
                                   "filas":len(otras),"solapamiento_exacto_con_csv_principal":solapadas,
                                   "evaluacion":sin_textos(evaluar(datos_evaluacion(otras,list(range(len(otras))),args.csv_adicional.name,"sondeo sintético adicional; independencia no acreditada"),modelo,medir=True))}
    verificar_artefactos(ROOT/"src/infrastructure/ai/models")
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    with args.salida.open("x",encoding="utf-8") as f:
        json.dump(informe,f,ensure_ascii=False,indent=2,allow_nan=False)
    print(json.dumps({"filas":len(filas),"particiones":[len(train),len(val),len(test)],"duplicados":pares_duplicados,"comparacion":comparacion},ensure_ascii=False))


if __name__ == "__main__":
    main()
