from scripts.carga_750_aislada import resumen


def test_metricas_separan_rechazos_esperados_de_fallos_reales():
    filas = [{"status": 200, "ok": True, "milisegundos": 10},
             {"status": 403, "ok": True, "milisegundos": 20},
             {"status": 500, "ok": False, "milisegundos": 30},
             {"status": None, "ok": False, "milisegundos": 40}]
    r = resumen(filas, 2)
    assert r["emitidas"] == 4 and r["completadas_http"] == 3
    assert r["fallidas"] == 2 and r["rechazos_esperados"] == 1
    assert r["tasa_error"] == .5 and r["throughput_http_s"] == 2
    assert r["latencia_ms"]["p50"] == 25
