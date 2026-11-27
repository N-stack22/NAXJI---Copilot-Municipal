from src.adapters.out.ai.fidelidad_inspeccion import atribuir_datos_aportados


def test_atribucion_conserva_referencia_y_observacion_sin_inventar_verificacion():
    contenido = {"actuaciones":"Resumen generado sin identificar la ficha", "conclusiones":"Comprobar antes de actuar"}
    datos = {"resultados_observados":"Dos bolsas cerradas; contenido desconocido", "referencias_conocidas":"E1: ficha ficticia, fotografía no revisada"}
    salida = atribuir_datos_aportados(contenido, datos, {"observaciones_aportadas":True})
    assert "E1: ficha ficticia, fotografía no revisada" in salida["actuaciones"]
    assert "Dos bolsas cerradas; contenido desconocido" in salida["actuaciones"]
    assert "no corroborados automáticamente" in salida["actuaciones"]
    assert "E1" not in contenido["actuaciones"]
    assert atribuir_datos_aportados(contenido, datos, None) == contenido
    assert atribuir_datos_aportados(contenido, datos, {"observaciones_aportadas":False}) == contenido
    citado = {**contenido, "actuaciones":"Datos según E1 aportada; requieren contraste"}
    assert atribuir_datos_aportados(citado, datos, {"observaciones_aportadas":True}) == citado
    assert atribuir_datos_aportados(contenido, {"resultados_observados":"Observación sin referencia identificada"}, {"observaciones_aportadas":True}) == contenido
