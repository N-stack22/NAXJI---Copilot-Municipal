import re
from src.domain.value_objects.seccion_salida import secciones_efectivas, CLAVES_TECNICAS


def secciones_revisables(version):
    secciones = [{"clave":s.clave,"titulo":s.titulo} for s in secciones_efectivas(version.secciones_salida)]
    if version.secciones_salida is None:
        conocidas = {s["clave"] for s in secciones} | CLAVES_TECNICAS
        secciones += [{"clave":k,"titulo":k.replace("_", " ").capitalize()} for k,v in version.contenido.items()
                      if k not in conocidas and isinstance(v,str)]
    return secciones


def advertencias_respaldo(version):
    """Indicadores estructurales; no afirman validez jurídica ni implicación semántica."""
    avisos = []
    fuentes = (version.sustento or {}).get("fuentes", [])
    for seccion in secciones_revisables(version):
        clave = seccion["clave"]
        texto = version.contenido.get(clave, "")
        if not isinstance(texto, str) or not texto.strip():
            avisos.append({"seccion": clave, "motivo": "Sección sin contenido; complete o justifique su omisión."})
            continue
        if re.search(r"pendiente|por verificar|no proporcionad|no acreditad|\[completar", texto, re.I):
            avisos.append({"seccion": clave, "motivo": "Contiene información pendiente de comprobación."})
        citas = [c for f in fuentes if not f.get("sin_acceso") for c in f.get("citas", [])
                 if c.get("seccion") == clave]
        if not citas:
            avisos.append({"seccion": clave, "motivo": "Sin cita documental accesible; contraste los datos y su sustento."})
        else:
            avisos.append({"seccion": clave, "motivo": "Compruebe que la fuente sustenta cada afirmación y sigue vigente."})
    if any(f.get("sin_acceso") for f in fuentes):
        avisos.append({"seccion": "fuentes", "motivo": "Hay fuentes sin acceso para este usuario; no puede verificarlas desde esta sesión."})
    return avisos
