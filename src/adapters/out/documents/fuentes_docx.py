def agregar_fuentes(documento, version):
    """Anexo de snapshots guardados: nunca recupera ni consulta servicios."""
    if not getattr(version, "sustento", None):
        return
    documento.add_heading("Fuentes de referencia de esta versión", level=1)
    documento.add_paragraph(version.sustento.get("advertencia", "Requiere revisión humana"))
    documento.add_paragraph("Resultado de recuperación: " + version.sustento["estado"])
    for fuente in version.sustento["fuentes"]:
        if fuente.get("sin_acceso"):
            documento.add_paragraph("Fuente con acceso actualmente restringido.")
            continue
        documento.add_paragraph(f"[F:{fuente['fragmento_id']}] {fuente['titulo']} · {fuente['localizacion']}")
        documento.add_paragraph("Procedencia: " + fuente["procedencia"])
        documento.add_paragraph("Citada" if fuente["citas"] else "Recuperada sin citar")
        documento.add_paragraph(fuente["texto"])
        for cita in fuente["citas"]:
            documento.add_paragraph(f"{cita['seccion']}: {cita['estado']}")
