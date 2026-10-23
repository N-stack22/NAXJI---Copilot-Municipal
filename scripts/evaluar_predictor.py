"""Evaluación offline; nunca entrena ni escribe artefactos del predictor.

Formato y límites: docs/EVALUACION_PREDICTOR.md.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, hamming_loss,
    multilabel_confusion_matrix, precision_recall_fscore_support,
)
from sklearn.preprocessing import MultiLabelBinarizer

from src.adapters.out.ai.sklearn_context_predictor import AREAS, TIPOS, SklearnContextPredictor, demo_id


def validar_datos(datos, etiquetas):
    if not isinstance(datos, dict) or set(datos) != {"metadata", "casos"}:
        raise ValueError("Se requieren metadata y casos")
    metadata = datos["metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("metadata debe ser un objeto")
    for clave in ("fuente", "etiquetado", "particion"):
        if not isinstance(metadata.get(clave), str) or not metadata[clave].strip():
            raise ValueError(f"Falta metadata.{clave}")
    if type(metadata.get("independiente_entrenamiento")) is not bool:
        raise ValueError("Declare metadata.independiente_entrenamiento como booleano")
    casos = datos["casos"]
    if not isinstance(casos, list) or not casos:
        raise ValueError("Se requiere al menos un caso etiquetado; cero casos no evalúan el modelo")
    ids, textos = set(), set()
    for caso in casos:
        if not isinstance(caso, dict) or set(caso) != {"id", "asunto", "tipo_informe", "area_destino", "temas_normativos"}:
            raise ValueError("Cada caso requiere id, asunto, tipo_informe, area_destino y temas_normativos")
        for clave in ("id", "asunto"):
            if not isinstance(caso[clave], str) or not caso[clave].strip():
                raise ValueError(f"Caso sin {clave} válido")
        texto = caso["asunto"].strip()
        if caso["id"] in ids or texto in textos:
            raise ValueError("No repita identificadores ni asuntos en la evaluación")
        ids.add(caso["id"])
        textos.add(texto)
        if caso["tipo_informe"] not in TIPOS or caso["area_destino"] not in AREAS:
            raise ValueError("Etiqueta de tipo o área desconocida; use los nombres documentados")
        temas = caso["temas_normativos"]
        if (not isinstance(temas, list) or any(not isinstance(t, str) for t in temas)
                or len(temas) != len(set(temas)) or set(temas) - set(etiquetas)):
            raise ValueError("Temas normativos desconocidos o repetidos")
    return casos


def inferir(predictor, asuntos):
    etiquetas = [str(e) for e in predictor.mlb.classes_]
    nombres = {demo_id(f"NORMATIVA:{e}"): e for e in etiquetas}
    resultados = []
    for asunto in asuntos:
        # Reproduce la normalización de CrearSolicitud antes de invocar el puerto.
        texto = asunto.strip()
        p = predictor.predecir(texto, uuid5(NAMESPACE_URL, "naxji:evaluacion:" + texto))
        probabilidades = predictor.modelo_normas.predict_proba(predictor.features_norm.transform([texto]))[0]
        resultados.append({
            "entrada": asunto, "entrada_normalizada": texto,
            "tipo_informe": p.parametros["tipo_predicho"], "area_destino": p.parametros["area_predicha"],
            "confianza_tipo": p.confianza_tipo, "confianza_area": p.confianza_area,
            "temas_normativos": [nombres[n.normativa_id] for n in p.normativas],
            "probabilidades_temas": dict(zip(etiquetas, map(float, probabilidades), strict=True)),
            "modelo": p.modelo, "version_modelo": p.version_modelo,
            "algoritmos": p.parametros["algoritmos"], "umbral_normas": predictor.umbral_normas,
            "validacion_humana": p.resultado_validacion.value,
        })
    return resultados


def metricas_categoria(reales, predichas, etiquetas):
    return {
        "accuracy": float(accuracy_score(reales, predichas)),
        "por_clase_y_promedios": classification_report(reales, predichas, labels=etiquetas, output_dict=True, zero_division=0),
        "etiquetas_matriz": etiquetas,
        "matriz_confusion": confusion_matrix(reales, predichas, labels=etiquetas).tolist(),
    }


def metricas_temas(reales, predichas, etiquetas):
    codificador = MultiLabelBinarizer(classes=etiquetas)
    y = codificador.fit_transform(reales)
    p = codificador.transform(predichas)
    promedios = {}
    for promedio in ("micro", "macro", "weighted", "samples"):
        precision, recall, f1, _ = precision_recall_fscore_support(y, p, average=promedio, zero_division=0)
        promedios[promedio] = {"precision": float(precision), "recall": float(recall), "f1": float(f1)}
    return {
        "accuracy_conjunto_exacto": float(accuracy_score(y, p)),
        "hamming_loss": float(hamming_loss(y, p)), "promedios": promedios,
        "por_clase_y_promedios": classification_report(y, p, target_names=etiquetas, output_dict=True, zero_division=0),
        "etiquetas_matrices": etiquetas,
        "matrices_confusion_por_etiqueta": multilabel_confusion_matrix(y, p).tolist(),
    }


def evaluar(datos, predictor=None):
    predictor = predictor or SklearnContextPredictor()
    etiquetas = [str(e) for e in predictor.mlb.classes_]
    casos = validar_datos(datos, etiquetas)
    predicciones = inferir(predictor, [c["asunto"] for c in casos])
    for caso, prediccion in zip(casos, predicciones, strict=True):
        prediccion["id"] = caso["id"]
        prediccion["referencia_etiquetada"] = {k: caso[k] for k in ("tipo_informe", "area_destino", "temas_normativos")}
    return {
        "schema_version": 1, "metadata_declarada": datos["metadata"], "numero_casos": len(casos),
        "independencia_verificada": False,
        "advertencias": [
            "La procedencia e independencia son declaraciones del proveedor de datos, no verificadas por este programa.",
            "No hay umbral académico de aceptación configurado. Estas métricas no certifican cumplimiento.",
            "Las clases con soporte cero se incluyen con métricas cero; revise soporte y representatividad.",
            "Memorando figura en el catálogo, pero no entre las clases del artefacto de tipo.",
        ],
        "clases_entrenadas": {"tipo_informe": list(map(str, predictor.modelo_tipo.classes_)),
                              "area_destino": list(map(str, predictor.modelo_area.classes_)), "temas": etiquetas},
        "metricas": {
            "tipo_informe": metricas_categoria([c["tipo_informe"] for c in casos], [p["tipo_informe"] for p in predicciones], list(TIPOS)),
            "area_destino": metricas_categoria([c["area_destino"] for c in casos], [p["area_destino"] for p in predicciones], list(AREAS)),
            "temas_normativos": metricas_temas([c["temas_normativos"] for c in casos], [p["temas_normativos"] for p in predicciones], etiquetas),
        }, "predicciones": predicciones,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", required=True, type=Path, help="JSON etiquetado según la documentación")
    parser.add_argument("--salida", required=True, type=Path, help="Archivo JSON nuevo; no sobrescribe archivos")
    args = parser.parse_args(argv)
    try:
        raw = args.datos.read_bytes()
        datos = json.loads(raw)
        resultado = evaluar(datos)
        resultado["sha256_datos"] = sha256(raw).hexdigest()
        modelos = ROOT / "src/infrastructure/ai/models"
        resultado["sha256_artefactos"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(modelos.iterdir()) if p.suffix in {".joblib", ".json"}}
        resultado["versiones"] = {"python": sys.version.split()[0], "numpy": np.__version__}
        import sklearn
        resultado["versiones"]["sklearn"] = sklearn.__version__
        contenido = json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        # No sustituir evidencia anterior, datos de entrada o modelos por error.
        with args.salida.open("x", encoding="utf-8") as archivo:
            archivo.write(contenido)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f"Evaluación no completada: {error}\n")
    print(f"Evaluados {resultado['numero_casos']} casos. Independencia no verificada; informe: {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
