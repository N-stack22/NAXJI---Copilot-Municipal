"""Criterios PMV3: decisiones de una etapa, permisos, snapshots y exportación sin IA."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from io import BytesIO
from uuid import uuid4
from unittest.mock import Mock

import pytest
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfReader

from src.domain.services.errores import ConflictoEstado, DatosInvalidos, NoAutorizado
from src.domain.value_objects.estados import Rol
from src.infrastructure.auth.mock import usuarios_demo
from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings
from src.adapters.out.ai.context_predictor_mock import ContextPredictorMock
from src.adapters.out.ai.generador_borrador_mock import GeneradorBorradorMock
from src.main import create_app
from tests.test_casos_uso import preparar


@pytest.fixture
def caso():
    config = Settings(pmv3_enabled=True)
    deps = Container(config, predictor=ContextPredictorMock(), generador=GeneradorBorradorMock())
    usuarios = usuarios_demo()
    autor = usuarios["demo-funcionario"]
    s = preparar(deps, autor)
    informe = deps.generar_borrador.ejecutar(s.id, autor)
    revisor = replace(usuarios["demo-revisor-pmv3"], area_id=s.area_destino_id)
    return config, deps, autor, revisor, informe


def comprobaciones(historial):
    return {a["seccion"]: "Contraste manual de los datos y fuentes del caso ficticio; prueba de software."
            for a in historial["versiones"][-1]["advertencias"]}


def aprobar(deps, autor, revisor, iid, numero=1):
    h = deps.revision.enviar(iid, autor, numero)
    return deps.revision.decidir(iid, revisor, numero, "APROBADO", "Revisión humana de prueba", comprobaciones(h))


def test_revision_edita_decide_una_vez_y_conserva_historia(caso):
    _, d, autor, r, informe = caso
    original = deepcopy(informe.versiones[0])
    h = d.revision.enviar(informe.id, autor, 1)
    assert h["estado"] == "EN_REVISION"
    assert h["versiones"][0]["advertencias"]
    cambios = {s["clave"]: "Texto corregido y comprobado para esta prueba." for s in h["versiones"][0]["secciones"]}
    h = d.revision.editar(informe.id, r, 1, cambios)
    assert h["versiones"][-1]["numero_version"] == 2
    assert h["versiones"][-1]["autor_id"] == r.id
    assert d.informes.obtener_por_id(informe.id).versiones[0] == original
    with pytest.raises(ConflictoEstado):
        d.revision.decidir(informe.id, r, 1, "APROBADO", "Obsoleto", comprobaciones(h))
    with pytest.raises(DatosInvalidos):
        d.revision.decidir(informe.id, r, 2, "APROBADO", "Sin comprobación", {})
    h = d.revision.decidir(informe.id, r, 2, "APROBADO", "Revisión humana", comprobaciones(h))
    assert h["estado"] == "APROBADO"
    assert [v["estado"] for v in h["versiones"]] == ["EN_REVISION", "APROBADO"]
    evento = h["eventos"][-1]
    assert evento["usuario_id"] == r.id and evento["fecha"] and evento["detalle"]["comprobaciones"]
    with pytest.raises(ConflictoEstado):
        d.revision.decidir(informe.id, r, 2, "RECHAZADO", "Segunda decisión", {})
    with pytest.raises(ConflictoEstado):
        d.revision.editar(informe.id, r, 2, cambios)


@pytest.mark.parametrize("identidad", ["demo-funcionario", "demo-admin", "demo-aprobador", "demo-otro", "demo-revisor"])
def test_solo_revisor_distinto_autor_y_del_area_decide(caso, identidad):
    _, d, autor, _, informe = caso
    h = d.revision.enviar(informe.id, autor, 1)
    with pytest.raises(NoAutorizado):
        d.revision.decidir(informe.id, usuarios_demo()[identidad], 1, "APROBADO", "Sin permiso", comprobaciones(h))


def test_fuera_de_area_no_lee_y_listado_filtra_antes_de_paginar(caso):
    _, d, autor, r, informe = caso
    otro = replace(r, area_id=uuid4())
    assert d.revision.listar(otro, 1) == []
    with pytest.raises(NoAutorizado):
        d.revision.historial(informe.id, otro)
    assert d.revision.listar(r, 1)[0]["id"] == informe.id
    assert d.revision.listar(autor, 1)[0]["id"] == informe.id
    with pytest.raises(NoAutorizado):
        d.revision.auditoria(r)
    assert d.revision.auditoria(usuarios_demo()["demo-admin"])[0]["accion"] == "CREAR_VERSION"


def test_rechazo_registra_motivo_y_bloquea_exportacion(caso):
    _, d, a, r, i = caso
    d.revision.enviar(i.id, a, 1)
    h = d.revision.decidir(i.id, r, 1, "RECHAZADO", "Falta evidencia del caso", {})
    assert h["versiones"][0]["estado"] == "RECHAZADO"
    assert h["eventos"][-1]["detalle"]["motivo"] == "Falta evidencia del caso"
    for formato in ("docx", "pdf"):
        with pytest.raises(ConflictoEstado):
            d.revision.exportar(i.id, 1, a, formato)


def test_error_evento_revierte_estado_y_version(caso):
    _, d, a, r, i = caso
    h = d.revision.enviar(i.id, a, 1)
    anterior = deepcopy(d.memoria.revisiones)
    original = d.revisiones.registrar
    def fallar(evento):
        original(evento)
        raise RuntimeError("Fallo de auditoría")
    d.revisiones.registrar = fallar
    with pytest.raises(RuntimeError):
        d.revision.decidir(i.id, r, 1, "APROBADO", "Prueba", comprobaciones(h))
    assert d.informes.obtener_por_id(i.id).estado.value == "EN_REVISION"
    assert d.memoria.revisiones == anterior


def test_decisiones_concurrentes_no_sobrescriben(caso):
    _, d, a, r, i = caso
    h = d.revision.enviar(i.id, a, 1)
    def decidir():
        try:
            d.revision.decidir(i.id, r, 1, "APROBADO", "Prueba", comprobaciones(h))
            return "ok"
        except ConflictoEstado:
            return "conflicto"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(lambda _: decidir(), range(2))) == ["conflicto", "ok"]


def test_exportaciones_contienen_snapshot_aprobado_sin_ia(caso):
    _, d, a, r, i = caso
    aprobar(d, a, r, i.id)
    d.generar_borrador.generador = Mock(generar=Mock(side_effect=AssertionError("No debe invocar IA")))
    docx = d.revision.exportar(i.id, 1, a, "docx")
    pdf = d.revision.exportar(i.id, 1, a, "pdf")
    documento = Document(BytesIO(docx))
    texto_word = " ".join(n.text or "" for n in documento.element.body.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
    texto_pdf = " ".join(p.extract_text() for p in PdfReader(BytesIO(pdf)).pages)
    normalizar = lambda s: " ".join(s.split())
    for seccion in i.versiones[0].secciones_salida:
        texto = i.versiones[0].contenido[seccion.clave]
        assert normalizar(texto) in normalizar(texto_word)
        assert normalizar(texto) in normalizar(texto_pdf)
    assert d.informes.obtener_por_id(i.id).versiones == i.versiones
    assert [e["detalle"]["formato"] for e in d.revisiones.eventos(i.id) if e["accion"] == "EXPORTAR"] == ["docx", "pdf"]


def test_fuente_revocada_no_se_puede_aprobar(caso):
    _, d, a, r, i = caso
    d.obtener_informe.documentos = Mock(proteger=lambda informe, usuario: informe)
    raw = d.informes.obtener_por_id(i.id)
    raw.versiones[0].sustento = {"fuentes": [{"sin_acceso": True, "citas": []}]}
    # Mutación directa exclusiva del fixture para simular un snapshot inaccesible.
    d.memoria.informes[i.id] = raw
    h = d.revision.enviar(i.id, a, 1)
    with pytest.raises(DatosInvalidos, match="sin acceso"):
        d.revision.decidir(i.id, r, 1, "APROBADO", "Prueba", comprobaciones(h))


def test_api_permiso_paginacion_flag_y_legacy_export(caso):
    config, d, a, r, i = caso
    with TestClient(create_app(config, d)) as c:
        c.headers["Authorization"] = "Bearer demo-funcionario"
        assert c.get("/revision/informes?limite=101").status_code == 422
        assert c.get("/auditoria").status_code == 403
        assert c.get(f"/informes/{i.id}/versiones/1/docx").status_code == 409
        assert c.post(f"/revision/informes/{i.id}/enviar", json={"numero_version": 1}).status_code == 200
        c.app.state.usuarios_demo["demo-revisor-pmv3"] = r
        c.headers["Authorization"] = "Bearer demo-revisor-pmv3"
        h = c.get(f"/revision/informes/{i.id}").json()
        response = c.post(f"/revision/informes/{i.id}/decidir", json={"numero_version": 1,
            "decision": "APROBADO", "motivo": "Prueba humana", "comprobaciones": comprobaciones(h)})
        assert response.status_code == 200, response.text
        assert c.get(f"/revision/informes/{i.id}/versiones/1/exportar?formato=pdf").content.startswith(b"%PDF")
        assert c.get(f"/revision/informes/{i.id}").headers["Cache-Control"] == "no-store"
    with TestClient(create_app(Settings(), Container(Settings(), predictor=ContextPredictorMock(), generador=GeneradorBorradorMock()))) as c:
        c.headers["Authorization"] = "Bearer demo-funcionario"
        assert c.get("/revision/config").json() == {"enabled": False}
        assert c.get("/revision/informes").status_code == 503
