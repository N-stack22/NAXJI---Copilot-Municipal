import re
from src.domain.value_objects.seccion_salida import secciones_efectivas


def advertencias_respaldo(version):
    """Indicadores estructurales; no afirman validez jurídica ni implicación semántica."""
    avisos = []
    fuentes = (version.sustento or {}).get("fuentes", [])
    for seccion in secciones_efectivas(version.secciones_salida):
        texto = version.contenido.get(seccion.clave, "")
        if not isinstance(texto, str) or not texto.strip():
            avisos.append({"seccion": seccion.clave, "motivo": "Sección sin contenido; complete o justifique su omisión."})
            continue
        if re.search(r"pendiente|por verificar|no proporcionad|no acreditad|\[completar", texto, re.I):
            avisos.append({"seccion": seccion.clave, "motivo": "Contiene información pendiente de comprobación."})
        citas = [c for f in fuentes if not f.get("sin_acceso") for c in f.get("citas", [])
                 if c.get("seccion") == seccion.clave]
        if not citas:
            avisos.append({"seccion": seccion.clave, "motivo": "Sin cita documental accesible; contraste los datos y su sustento."})
        else:
            avisos.append({"seccion": seccion.clave, "motivo": "Compruebe que la fuente sustenta cada afirmación y sigue vigente."})
    if any(f.get("sin_acceso") for f in fuentes):
        avisos.append({"seccion": "fuentes", "motivo": "Hay fuentes sin acceso para este usuario; no puede verificarlas desde esta sesión."})
    return avisos
