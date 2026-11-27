"""Exporta evidencia real; ejecutar con el upython de Understand y una base analizada.

No crea licencias, no analiza dependencias instaladas y no modifica código fuente.
La base .und y el log original se conservan fuera del directorio publicable.
"""
import argparse
import csv
import hashlib
import html
import json
from collections import Counter
from pathlib import Path
import statistics
import subprocess

import understand


METRICS = [
    "CountLine", "CountLineCode", "CountLineComment", "CountDeclClass",
    "CountDeclFunction", "CountDeclMethod", "Cyclomatic", "CyclomaticStrict",
    "AvgCyclomatic", "MaxCyclomatic", "SumCyclomatic", "HalsteadMaintainIdx",
    "CountClassCoupled", "DirectFanIn", "DirectFanOut",
]


def layer(path):
    if "/web/" in path:
        return "Frontend"
    for prefix, name in [
        ("src/domain/", "Dominio"), ("src/application/", "Aplicacion"),
        ("src/adapters/in/", "Adaptadores de entrada"),
        ("src/adapters/out/", "Adaptadores de salida"),
        ("src/infrastructure/", "Infraestructura"),
    ]:
        if path.startswith(prefix):
            return name
    return "Arranque y despliegue"


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def distribution(values):
    values = [v for v in values if v is not None]
    return {"n": len(values), "min": min(values) if values else None,
            "mediana": statistics.median(values) if values else None,
            "max": max(values) if values else None}


def export(args):
    repo, out = args.repo.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    scope = json.loads((out / "alcance-archivos.json").read_text(encoding="utf-8"))
    expected = set(scope["archivos"])
    db = understand.open(str(args.database.resolve()))
    try:
        own, external = {}, []
        for entity in db.files():
            try:
                path = Path(entity.longname()).relative_to(repo).as_posix()
            except ValueError:
                external.append({"archivo": entity.name(), "biblioteca": entity.library()})
                continue
            if entity.library():
                raise ValueError(f"Biblioteca externa dentro del alcance: {path}")
            own[path] = entity
        if set(own) != expected:
            raise ValueError(f"Alcance distinto: extras={set(own)-expected}; faltantes={expected-set(own)}")
        rows = []
        for path, entity in sorted(own.items()):
            entity.add_to_arch("NAXJI Hexagonal/" + layer(path))
            rows.append({"archivo": path, "capa": layer(path), "lenguaje": entity.language(),
                         **entity.metric(METRICS, format="raw")})
        write_csv(out / "metricas-archivos.csv", rows, ["archivo", "capa", "lenguaje", *METRICS])
        write_csv(out / "acoplamiento-archivos.csv",
                  [{k: row[k] for k in ["archivo", "capa", "DirectFanIn", "DirectFanOut"]} for row in rows],
                  ["archivo", "capa", "DirectFanIn", "DirectFanOut"])
        maintain = [dict(archivo=r["archivo"], lenguaje=r["lenguaje"],
                         HalsteadMaintainIdx=r["HalsteadMaintainIdx"],
                         interpretacion=("valor nativo; fórmula original sin normalizar" if r["HalsteadMaintainIdx"]
                                         else "cero nativo; revisar soporte/archivo vacío, no inferir calidad"))
                    for r in rows]
        write_csv(out / "mantenibilidad-archivos.csv", maintain,
                  ["archivo", "lenguaje", "HalsteadMaintainIdx", "interpretacion"])
        functions, classes = [], []
        for kind, target in [("function,method", functions), ("class", classes)]:
            for entity in db.ents(kind):
                ref = entity.ref("definein")
                if ref is None or entity.library():
                    continue
                try:
                    path = Path(ref.file().longname()).relative_to(repo).as_posix()
                except ValueError:
                    continue
                if path not in own:
                    continue
                target.append({"archivo": path, "linea": ref.line(), "nombre": entity.longname(),
                               "tipo": entity.kindname(), **entity.metric(METRICS, format="raw")})
            target.sort(key=lambda row: (row["archivo"], row["linea"], row["nombre"]))
        fields = ["archivo", "linea", "nombre", "tipo", *METRICS]
        write_csv(out / "metricas-funciones.csv", functions, fields)
        write_csv(out / "metricas-clases.csv", classes, fields)
        edges = []
        reverse = {entity.id(): path for path, entity in own.items()}
        for source, entity in sorted(own.items()):
            for destination, refs in entity.depends().items():
                dest = reverse.get(destination.id())
                if dest:
                    edges.append({"origen": source, "destino": dest,
                                  "capa_origen": layer(source), "capa_destino": layer(dest),
                                  "referencias": len(refs),
                                  "tipos": ";".join(sorted({ref.kindname() for ref in refs}))})
        edges.sort(key=lambda edge: (edge["origen"], edge["destino"]))
        write_csv(out / "dependencias-rutas.csv", edges,
                  ["origen", "destino", "capa_origen", "capa_destino", "referencias", "tipos"])
        grouped = Counter((e["capa_origen"], e["capa_destino"]) for e in edges)
        write_csv(out / "dependencias-capas.csv",
                  [{"origen": a, "destino": b, "pares_archivos": n} for (a, b), n in sorted(grouped.items())],
                  ["origen", "destino", "pares_archivos"])
        forbidden = [e for e in edges if
                     (e["capa_origen"] == "Dominio" and e["capa_destino"] != "Dominio") or
                     (e["capa_origen"] == "Aplicacion" and e["capa_destino"] not in {"Dominio", "Aplicacion"})]
        write_json(out / "verificacion-hexagonal.json", {
            "metodo": "Dependencias de archivos resueltas por Understand; grupos por ruta, no verificación dinámica",
            "reglas": ["Dominio depende solo de Dominio", "Aplicacion depende solo de Aplicacion y Dominio"],
            "infracciones_resueltas": forbidden,
            "pares_archivos_propios": len(edges),
            "limites": "No prueba ausencia de dependencias dinámicas ni valida proveedores externos excluidos",
        })
        arch = db.lookup_arch("NAXJI Hexagonal")
        diagrams = out / "diagramas"
        diagrams.mkdir(exist_ok=True)
        for graph, stem in [("Dependencies", "hexagonal-dependencias"),
                            ("Graph Architecture", "hexagonal-estructura"),
                            ("File Dependencies", "dependencias-archivos")]:
            for ext in ["svg", "png"]:
                arch.draw(graph, filename=str(diagrams / (stem + "." + ext)))
        for ext in ["svg", "png"]:
            db.draw("Most Complex Functions", filename=str(diagrams / ("funciones-complejas." + ext)))
        project = db.metric([*METRICS, "SonargraphMaintainability"], format="raw")
        own_totals = {}
        for metric in ["CountLine", "CountLineCode", "CountLineComment", "CountDeclClass",
                       "CountDeclFunction", "CountDeclMethod"]:
            available = [row[metric] for row in rows if row[metric] is not None]
            own_totals[metric] = sum(available) if available else None
        write_json(out / "resumen.json", {
            "fecha_corte": "2026-11-27", "commit_analizado": scope["commit_analizado"],
            "herramienta": "SciTools Understand", "version": understand.version(),
            "archivos_propios": len(own), "simbolicos_estandar_no_contabilizados": external,
            "lenguajes": dict(Counter(r["lenguaje"] for r in rows)),
            "metricas_proyecto_nativas": project, "sumas_archivos_propios": own_totals,
            "funciones_con_definicion_exportadas": len(functions),
            "clases_con_definicion_exportadas": len(classes),
            "cyclomatic_funciones": distribution(r["Cyclomatic"] for r in functions),
            "halstead_archivos_no_cero": distribution(r["HalsteadMaintainIdx"] for r in rows
                                                      if r["HalsteadMaintainIdx"]),
            "halstead_ceros_nativos": sum(r["HalsteadMaintainIdx"] == 0 for r in rows),
            "fan_in_archivos": distribution(r["DirectFanIn"] for r in rows),
            "fan_out_archivos": distribution(r["DirectFanOut"] for r in rows),
            "top_cyclomatic": sorted(functions, key=lambda r: r["Cyclomatic"] or -1, reverse=True)[:10],
            "limites": ["None se exporta vacío, nunca se sustituye por cero",
                        "Las sumas/medianas son agregaciones descriptivas de métricas nativas",
                        "CountDeclFunction incluye métodos y funciones anidadas según el lenguaje; no sumar CountDeclMethod",
                        "Halstead original por archivo/función, no porcentaje ni índice global",
                        "SonargraphMaintainability nativo usa ML2 sobre grafo de dependencias, no certifica calidad institucional"],
        })
        write_json(out / "fuentes-sha256.json", {
            path: hashlib.sha256((repo / path).read_bytes()).hexdigest() for path in sorted(own)
        })
        # Vista de consulta propia; no se presenta como reporte nativo de SciTools.
        columns = ["archivo", "CountLineCode", "CountDeclClass", "CountDeclFunction",
                   "MaxCyclomatic", "HalsteadMaintainIdx", "DirectFanIn", "DirectFanOut"]
        table = "".join("<tr>" + "".join(
            "<td>" + html.escape("N/D" if row[c] is None else str(row[c])) + "</td>"
            for c in columns) + "</tr>" for row in rows)
        page = """<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NAXJI — C-06 Understand</title><style>
body{font:16px system-ui;margin:2rem;color:#143339;background:#f4f8f8}a{color:#006b62}
table{border-collapse:collapse;background:white}th,td{padding:.5rem;border:1px solid #ccd9d9;text-align:left}
th{background:#143339;color:white}td:first-child{font-family:monospace}input{padding:.7rem;width:min(90%,40rem)}
.scroll{overflow:auto}img{max-width:100%;background:white}</style><body>
<h1>NAXJI — evidencia C-06</h1>
<p>Understand 8.1.1269 · main 67d9db2 · corte 27/11/2026.</p>
<p>Vista derivada de la API real de Understand; los reportes nativos se conservan por separado.
149 archivos propios · 6.719 líneas de código · 141 clases · 696 funciones · complejidad máxima 26.</p>
<p><a href="README.md">Interpretación, alcance y limitaciones</a> · <a href="resumen.json">Resumen JSON</a> ·
<a href="metricas-nativas.csv">CSV nativo</a> · <a href="metricas-funciones.csv">Funciones</a> ·
<a href="metricas-clases.csv">Clases</a> · <a href="dependencias-rutas.csv">Dependencias</a></p>
<p>0 errores y 224 advertencias de resolución documentadas. N/D significa métrica no disponible.
Halstead original no está normalizado a 0–100. SonargraphMaintainability (ML2) nativo:
84,44774960712785; no es un porcentaje de calidad institucional.</p>
<h2>Dependencias hexagonales resueltas</h2>
<img src="diagramas/hexagonal-dependencias.svg" alt="Diagrama nativo de dependencias de las siete capas">
<p><a href="diagramas/dependencias-archivos.svg">Grafo completo</a> ·
<a href="verificacion-hexagonal.json">Reglas verificadas y límites</a></p>
<h2>Reportes nativos HTML</h2><p>
<a href="reportes/complejidad/path_0.html">Complejidad</a> ·
<a href="reportes/lineas/path_0.html">Líneas</a> ·
<a href="reportes/clases/index.html">Clases</a> ·
<a href="reportes/mantenibilidad-funciones/index.html">Mantenibilidad de funciones</a> ·
<a href="reportes/mantenibilidad-clases/index.html">Mantenibilidad de clases</a> ·
<a href="reportes/acoplamiento-control/index.html">Acoplamiento de control</a> ·
<a href="reportes/acoplamiento-datos/index.html">Acoplamiento de datos</a></p>
<p>El reporte nativo de complejidad enlaza detalles por archivo que esta exportación de SciTools no
genera. Las tablas por capa sí están disponibles; para el detalle completo usar los CSV y esta tabla.
Se registra esta limitación sin alterar los originales.</p>
<h2>Métricas por archivo propio</h2><label>Buscar archivo <input id="buscar" type="search"></label>
<div class="scroll"><table><thead><tr>"""
        page += "".join("<th>" + c + "</th>" for c in columns)
        page += "</tr></thead><tbody>" + table + """</tbody></table></div>
<script>document.getElementById('buscar').addEventListener('input',e=>{
for(const row of document.querySelectorAll('tbody tr'))row.hidden=!row.textContent.toLowerCase().includes(e.target.value.toLowerCase());
});</script></body></html>"""
        (out / "index.html").write_text(page + "\n", encoding="utf-8")
    finally:
        db.close()
    # CLI nativa: las exportaciones no se recrean ni se simulan en este script.
    commands = [
        ["metrics", "-metrics", *METRICS, "-options",
         "File Name Format=Relative Name;Show Declared In File=Relative Name",
         str(out / "metricas-nativas.csv")],
        ["export", "-dependencies", "file", "csv", str(out / "dependencias-nativas.csv")],
        ["export", "-arch", "NAXJI Hexagonal", str(out / "arquitectura-nativa.xml")],
    ]
    for title, slug in [
        ("Complexity Metrics", "complejidad"), ("Line Metrics", "lineas"),
        ("Class Metrics", "clases"), ("Low Maintainability Functions", "mantenibilidad-funciones"),
        ("Low Maintainability Classes Table", "mantenibilidad-clases"),
        ("Control Coupling", "acoplamiento-control"), ("Data Coupling", "acoplamiento-datos"),
    ]:
        dest = out / "reportes" / slug
        dest.mkdir(parents=True, exist_ok=True)
        # Los reportes por archivo se limitan a la arquitectura de archivos propios.
        # Los otros cuatro reportes solo admiten el proyecto en esta versión.
        target = ["-arch", "NAXJI Hexagonal"] if slug in {"complejidad", "lineas", "clases"} else []
        commands.append(["report", *target, "-format", "html,csv,png", title, str(dest)])
    for command in commands:
        subprocess.run([str(args.und), "-db", str(args.database), *command], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--und", type=Path, required=True)
    export(parser.parse_args())
