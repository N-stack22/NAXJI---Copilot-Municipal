"""Huellas de los artefactos versionados en d99f960; no certifican su entrenamiento."""
from hashlib import sha256

HUELLAS = {
    'features_norm.joblib': '7f544c2908808d30d943dc56ae2c703b8f8d82bba1373644958eb5fb5b842bb7',
    'mlb.joblib': '38a12ae14e9412c113e21c4b483820af2b735531250c67f064f884556404d924',
    'model_config.json': '12e4368b213803b054b2605ed87d75e699c5067b9fed159916d0eb83fe837b17',
    'modelo_area.joblib': 'fcb58df2ac8a32d4b3e66b65f55a3897a7515821e285b6dbbde35246e52912dc',
    'modelo_normas.joblib': '1841c25b9144572347e5186b9c9f8964293cb3bafa0abec42434e853298630e4',
    'modelo_tipo.joblib': '153c18fd25f250be0522f5b71cd3378bc86af772cb44faecc7c9dcac9d5c8113',
}


def verificar_artefactos(directorio):
    for nombre, esperado in HUELLAS.items():
        contenido = (directorio / nombre).read_bytes()
        # Git puede convertir saltos del JSON en Windows. Joblib siempre binario;
        # configuración se contrasta con LF, sin alterar los archivos originales.
        if nombre.endswith('.json'):
            contenido = contenido.replace(b'\r\n', b'\n')
        if sha256(contenido).hexdigest() != esperado:
            raise ValueError("El artefacto del predictor no coincide con la huella versionada: " + nombre)
