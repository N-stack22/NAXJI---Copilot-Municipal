"""Huellas de los artefactos versionados en d99f960; no certifican su entrenamiento."""
from hashlib import sha256

HUELLAS = {'features_norm.joblib': '7f544c2908808d30d943dc56ae2c703b8f8d82bba1373644958eb5fb5b842bb7', 'mlb.joblib': '38a12ae14e9412c113e21c4b483820af2b735531250c67f064f884556404d924', 'model_config.json': '0bc37219ced6f93b198e3a7b6fe87b781d51f3832892f45a8e938cb69496fdf1', 'modelo_area.joblib': 'fcb58df2ac8a32d4b3e66b65f55a3897a7515821e285b6dbbde35246e52912dc', 'modelo_normas.joblib': '1841c25b9144572347e5186b9c9f8964293cb3bafa0abec42434e853298630e4', 'modelo_tipo.joblib': '153c18fd25f250be0522f5b71cd3378bc86af772cb44faecc7c9dcac9d5c8113'}


def verificar_artefactos(directorio):
    for nombre, esperado in HUELLAS.items():
        if sha256((directorio / nombre).read_bytes()).hexdigest() != esperado:
            raise ValueError("El artefacto del predictor no coincide con la huella versionada: " + nombre)
