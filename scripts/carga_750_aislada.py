"""750 llamadas HTTP reales en laboratorio efímero; sin destino externo configurable.

PostgreSQL/pgvector y sklearn reales. Auth, Storage, LLM y embeddings DOBLES.
No estima capacidad de Ollama ni certifica producción. No lee .env.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
from threading import Event, Thread
from time import perf_counter, sleep

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import httpx
import numpy as np
import psutil
import uvicorn
from src.application.ports.input.solicitud_use_case import DatosSolicitud
from tests.entorno_cierre import entorno_aislado, solicitud_lista
from scripts.evidencia_cierre import huella_fuentes


def resumen(registros, segundos):
    valores = [r["milisegundos"] for r in registros]
    return {"emitidas": len(registros), "completadas_http": sum(r["status"] is not None for r in registros),
            "correctas_segun_caso": sum(r["ok"] for r in registros), "fallidas": sum(not r["ok"] for r in registros),
            "rechazos_esperados": sum(r["ok"] and r["status"] >= 400 for r in registros),
            "tasa_error": sum(not r["ok"] for r in registros)/len(registros) if registros else None,
            "throughput_http_s": len(registros)/segundos if segundos else None,
            "latencia_ms": dict(zip(["p50", "p95", "p99"], map(float, np.percentile(valores, [50, 95, 99])))) if valores else {}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pg-port", type=int, required=True)
    parser.add_argument("--salida", type=Path, required=True, help="Directorio nuevo de evidencia")
    parser.add_argument("--concurrencia", type=int, default=4, choices=range(1, 9))
    args = parser.parse_args()
    args.salida.mkdir(parents=True, exist_ok=False)
    huella = huella_fuentes(args.salida)
    inicio = datetime.now(timezone.utc).isoformat()
    resultados, recursos = [], []
    proceso = psutil.Process()
    parar = Event()
    def medir():
        proceso.cpu_percent()
        while not parar.wait(.2):
            recursos.append({"utc": datetime.now(timezone.utc).isoformat(), "rss_bytes_arnes_api": proceso.memory_info().rss,
                             "cpu_porcentaje_arnes_api": proceso.cpu_percent(), "cpu_porcentaje_host": psutil.cpu_percent()})
    monitor = Thread(target=medir, daemon=True)
    monitor.start()
    ultimo = {}
    def op(familia, metodo, ruta, esperado=200, usuario="autor", **kwargs):
        return {"familia": familia, "metodo": metodo, "ruta": ruta, "esperado": esperado, "usuario": usuario, "kwargs": kwargs}
    try:
        with entorno_aislado(args.pg_port) as entorno:
            d, autor = entorno.deps, entorno.usuarios["autor"]
            simple = [d.crear_solicitud.ejecutar(autor, DatosSolicitud(f"Solicitud ficticia para predicción {i}: residuos en parque")) for i in range(50)]
            listos = [solicitud_lista(entorno, i) for i in range(20)]
            informes = [d.generar_borrador.ejecutar(s, autor) for s in listos[:10]]
            plantilla = next(p for p in d.plantillas.listar() if p.version == 2 and "Piloto NAXJI" in p.nombre)
            servidor = uvicorn.Server(uvicorn.Config(entorno.app, host="127.0.0.1", port=0, log_level="error", access_log=False))
            sock = socket.socket(); sock.bind(("127.0.0.1", 0)); puerto = sock.getsockname()[1]
            hilo = Thread(target=servidor.run, kwargs={"sockets": [sock]}, daemon=True); hilo.start()
            limite = perf_counter()+10
            while not servidor.started and perf_counter() < limite:
                sleep(.02)
            if not servidor.started:
                raise RuntimeError("No se inició el servidor local de pruebas")
            base = f"http://127.0.0.1:{puerto}"
            contador = 0
            def fase(operaciones):
                nonlocal contador
                pendientes = []
                for item in operaciones:
                    contador += 1
                    item["id"] = f"TX-{contador:04d}"
                    pendientes.append(item)
                def llamada(item):
                    inicio_llamada = perf_counter()
                    respuesta, dato, error = None, None, None
                    try:
                        with httpx.Client(base_url=base, timeout=60, trust_env=False) as client:
                            respuesta = client.request(item["metodo"], item["ruta"],
                                headers={"Authorization": "Bearer laboratorio-"+item["usuario"]}, **item["kwargs"])
                            if "application/json" in respuesta.headers.get("content-type", ""):
                                dato = respuesta.json()
                    except Exception as exc:
                        error = type(exc).__name__
                    status = respuesta.status_code if respuesta is not None else None
                    resultado = {k: item[k] for k in ("id", "familia", "metodo", "ruta", "esperado")}
                    resultado.update(status=status, ok=status == item["esperado"], milisegundos=(perf_counter()-inicio_llamada)*1000,
                                     error=error, bytes=len(respuesta.content) if respuesta is not None else 0)
                    return resultado, dato
                with ThreadPoolExecutor(max_workers=args.concurrencia) as pool:
                    for registro, dato in pool.map(llamada, pendientes):
                        resultados.append(registro)
                        ultimo[registro["id"]] = dato
                (args.salida/"transacciones.jsonl").write_text("".join(json.dumps(r)+"\n" for r in resultados), encoding="utf-8")
                print(f"{len(resultados)}/750; fallos inesperados: {sum(not r['ok'] for r in resultados)}", flush=True)
                return resultados[-len(pendientes):]
            try:
                inicio_carga = perf_counter()
                # G1: 150 accesos/consultas. Sesiones representadas por identidad de prueba.
                fase([op("G1", "GET", "/auth/me", 401 if i < 10 else 200, "invalido" if i < 10 else "autor") for i in range(50)]
                     + [op("G1", "GET", "/plantillas") for _ in range(50)]
                     + [op("G1", "GET", ruta) for ruta in ("/areas", "/tipos-informe") for _ in range(25)])
                # G2: 200 solicitudes válidas, inválidas y consultas de propiedad.
                fase([op("G2", "POST", "/solicitudes", 201, json={"asunto": f"Transacción sintética única {i}"}) for i in range(100)]
                     + [op("G2", "POST", "/solicitudes", 422, json={}) for _ in range(50)]
                     + [op("G2", "GET", f"/solicitudes/{s.id}", 200 if i < 25 else 403, "autor" if i < 25 else "otro") for i,s in enumerate(simple)])
                # G3: 150 predicciones/confirmaciones/consultas; sklearn REAL.
                registros = fase([op("G3", "POST", f"/solicitudes/{s.id}/predecir-contexto") for s in simple])
                fase([op("G3", "POST", f"/solicitudes/{s.id}/validar-prediccion", json={"prediccion_id": ultimo[r["id"]]["id"],
                          "resultado": "CORREGIDA", "tipo_informe_id": str(plantilla.tipo_informe_id),
                          "area_destino_id": str(entorno.area), "normativa_ids": []}) for s,r in zip(simple, registros)])
                fase([op("G3", "GET", f"/solicitudes/{s.id}/contexto") for s in simple])
                # G4: 150 llamadas de edición/revisión/historial/exportación y generación DOBLE.
                contenidos = [{s.clave: "Contenido corregido en prueba sintética de carga." for s in i.versiones[0].secciones_salida} for i in informes]
                fase([op("G4", "PUT", f"/informes/{i.id}", json={"numero_version": 1, "contenido": contenido}) for i,contenido in zip(informes, contenidos)])
                fase([op("G4", "POST", f"/revision/informes/{i.id}/enviar", json={"numero_version": 2}) for i in informes])
                fase([op("G4", "POST", f"/revision/informes/{i.id}/editar", usuario="revisor", json={"numero_version": 2, "contenido": contenido}) for i,contenido in zip(informes, contenidos)])
                fase([op("G4", "POST", f"/revision/informes/{i.id}/decidir", usuario="revisor", json={"numero_version": 3,
                     "decision": "APROBADO" if n < 5 else "RECHAZADO", "motivo": "SIMULACION de decisión para probar software; no revisión institucional",
                     "comprobaciones": {s.clave: "SIMULACION de contraste de datos ficticios" for s in i.versiones[0].secciones_salida} if n < 5 else {}}) for n,i in enumerate(informes)])
                fase([op("G4", "GET", f"/revision/informes/{i.id}/versiones/3/exportar?formato={formato}", 200 if n < 5 else 409)
                      for n,i in enumerate(informes) for formato in ("docx", "pdf")])
                fase([op("G4", "GET", f"/revision/informes/{i.id}") for _ in range(2) for i in informes]
                    + [op("G4", "GET", "/revision/informes") for _ in range(10)]
                    + [op("G4", "GET", "/auditoria", usuario="admin") for _ in range(10)]
                    + [op("G4", "GET", "/auditoria", 403) for _ in range(10)]
                    + [op("G4", "POST", f"/solicitudes/{s}/generar-borrador", 201, json={}) for s in listos[10:]]
                    + [op("G4", "GET", f"/informes/{i.id}") for i in informes]
                    + [op("G4", "GET", f"/informes/{i.id}/versiones/1") for i in informes]
                    + [op("G4", "POST", f"/revision/informes/{i.id}/decidir", 403, json={"numero_version": 3, "decision": "APROBADO", "motivo": "Sin permiso"}) for i in informes])
                # G5: 100 documentos/fragmentos/recuperación; Storage/embeddings DOBLES.
                registros = fase([op("G5", "POST", "/documentos", 201, files={"archivo": (f"fuente-{i}.txt", f"Fuente sintética {i}: criterios ambientales de residuos en parques. No acredita hechos.".encode(), "text/plain")},
                    data={"titulo": f"Fuente de carga {i}", "procedencia": "Corpus sintético de laboratorio", "ambito": "PRIVADO"}) for i in range(20)])
                documentos = [ultimo[r["id"]]["id"] for r in registros]
                fase([op("G5", "POST", f"/documentos/{did}/procesar") for did in documentos])
                fase([op("G5", "POST", "/documentos/recuperar", json={"consulta": "criterios ambientales de residuos en parques"}) for _ in range(20)]
                    + [op("G5", "GET", "/documentos") for _ in range(20)]
                    + [op("G5", "GET", f"/documentos/{did}/original", 200 if n < 10 else 404, "autor" if n < 10 else "otro") for n,did in enumerate(documentos)])
                duracion = perf_counter()-inicio_carga
                assert len(resultados) == 750 and len({r["id"] for r in resultados}) == 750
                informe = {"inicio_utc": inicio, "fin_utc": datetime.now(timezone.utc).isoformat(),
                    "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    "fuentes_manifest_sha256": huella,
                    "definicion": "Una transacción = una llamada HTTP medida; preparación y arranque excluidos",
                    "planificadas": 750, "no_ejecutadas": 750-len(resultados), "concurrencia_maxima": args.concurrencia,
                    "ramp_up": "Sin rampa; pool fijo por fase dependiente", "duracion_carga_s": duracion,
                    "dobles": ["Identidad/Auth", "Storage en memoria", "LLM determinista", "Embeddings no semánticos", "decisión humana simulada"],
                    "reales": ["HTTP loopback", "FastAPI", "sklearn LogisticRegression versionado", "PostgreSQL", "pgvector", "DOCX/PDF"],
                    "limites": "No mide capacidad de Ollama, Auth/Storage reales, RLS de Supabase ni aceptación humana. No es un ensayo de producción.",
                    "hardware": {"os": platform.platform(), "python": platform.python_version(), "procesador": platform.processor(),
                                 "cpu_logicas": os.cpu_count(), "ram_host_bytes": psutil.virtual_memory().total},
                    "total": resumen(resultados, duracion),
                    "familias": {g: resumen([r for r in resultados if r["familia"] == g], duracion) for g in ("G1", "G2", "G3", "G4", "G5")},
                    "recursos": {"alcance": "Proceso Python: arnés y API juntos; excluye contenedor PostgreSQL y GPU",
                                 "rss_max_bytes": max((r["rss_bytes_arnes_api"] for r in recursos), default=None),
                                 "cpu_max_porcentaje_arnes_api": max((r["cpu_porcentaje_arnes_api"] for r in recursos), default=None)}}
                (args.salida/"resultado.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
                (args.salida/"recursos.json").write_text(json.dumps(recursos, indent=2), encoding="utf-8")
                print(json.dumps(informe["total"], indent=2), flush=True)
            finally:
                servidor.should_exit = True
                hilo.join(timeout=10)
                sock.close()
    finally:
        parar.set(); monitor.join(timeout=2)
    return 0 if resultados and all(r["ok"] for r in resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
