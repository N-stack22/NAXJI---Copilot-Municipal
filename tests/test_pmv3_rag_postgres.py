"""Integra PMV2/PMV3: fuentes por versión, decisión y ambas exportaciones."""
from dataclasses import replace
from io import BytesIO
import os
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from docx import Document
from pypdf import PdfReader
import pytest

from src.adapters.out.ai.context_predictor_mock import ContextPredictorMock
from src.adapters.out.ai.generador_borrador_mock import GeneradorBorradorMock
from src.application.ports.input.solicitud_use_case import DatosSolicitud
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.services.errores import DatosInvalidos
from src.domain.value_objects.estados import ResultadoValidacion, Rol
from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings
from tests.test_pmv2_postgres import pmv2_db  # noqa: F401
from tests.test_estructura_postgres import db_local  # noqa: F401
from tests.test_pmv2 import cargar
from tests.test_pmv3 import comprobaciones

pytestmark = pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL/pgvector aislado: opt-in")
ROOT = Path(__file__).resolve().parents[1]


def test_fuentes_citadas_editadas_y_exportadas_sin_nueva_inferencia(pmv2_db):
    db, gestor, _, autor, _ = pmv2_db
    with db.connect(autocommit=True) as c:
        for archivo in ("database/migrations/20261126_01_pmv3_revision.sql", "database/seeds/20261126_plantillas_complementarias_piloto.sql"):
            c.execute((ROOT/archivo).read_text(encoding="utf-8"))
        rid = uuid4()
        c.execute("INSERT INTO auth.users VALUES (%s)", (rid,))
        c.execute("INSERT INTO perfiles(id,nombres,apellidos) VALUES (%s,'Revisor','Prueba')", (rid,))
    revisor = UsuarioActual(rid, frozenset({Rol.REVISOR}), autor.area_id)
    generador = GeneradorBorradorMock()
    def citado(*args):
        salida = generador.generar(*args)
        fuente = args[3].fuentes[0]
        return replace(salida, citas=tuple({"fragmento_id":fuente["fragmento_id"], "seccion":clave} for clave in salida.contenido))
    d = Container(Settings(persistence_mode="postgres", auth_mode="disabled", pmv3_enabled=True), database_settings=db,
                  predictor=ContextPredictorMock(), generador=Mock(generar=citado), documentos=gestor)
    doc = cargar(gestor, autor, texto="Referencia sintética ambiental: criterios documentales para parques y residuos.", ambito="AREA")
    gestor.procesar(doc.id, autor)
    s = d.crear_solicitud.ejecutar(autor, DatosSolicitud("Inspección ambiental de un parque"))
    p = d.predecir_contexto.ejecutar(s.id, autor)
    plantilla = next(p for p in d.plantillas.listar() if p.nombre == "Informe Técnico – Piloto NAXJI")
    d.validar_prediccion.ejecutar(s.id, autor, p.id, ResultadoValidacion.CORREGIDA, plantilla.tipo_informe_id, autor.area_id, [])
    d.actualizar_solicitud.ejecutar(s.id, autor, {"plantilla_id":plantilla.id})
    d.guardar_valores.ejecutar(s.id, autor, {c.id:"2026-11-26" if c.tipo_dato.value == "date" else "Datos ficticios de prueba" for c in plantilla.campos if c.obligatorio})
    informe = d.generar_borrador.ejecutar(s.id, autor, usar_documentos=True)
    original = informe.versiones[0].sustento
    h = d.revision.enviar(informe.id, autor, 1)
    cambios = {s["clave"]:h["versiones"][0]["contenido"][s["clave"]]+" Edición de revisión." for s in h["versiones"][0]["secciones"]}
    h = d.revision.editar(informe.id, revisor, 1, cambios)
    assert all(c["estado"] == "TEXTO_MODIFICADO" for f in h["versiones"][1]["sustento"]["fuentes"] for c in f["citas"])
    d.revision.decidir(informe.id, revisor, 2, "APROBADO", "Contraste simulado, exclusivo del caso de prueba", comprobaciones(h))
    d.generar_borrador.generador = None
    gestor.embeddings.fallar = True
    word = Document(BytesIO(d.revision.exportar(informe.id, 2, autor, "docx")))
    pdf = PdfReader(BytesIO(d.revision.exportar(informe.id, 2, autor, "pdf")))
    for texto in (" ".join(p.text for p in word.paragraphs), " ".join(p.extract_text() for p in pdf.pages)):
        assert "Referencia sintética ambiental" in texto
        assert "Edición de revisión." in texto
    assert d.informes.obtener_por_id(informe.id).versiones[0].sustento == original


def test_semillas_legales_y_memo_no_modifican_registros_existentes(db_local):
    db, _, _, _, _ = db_local
    archivo = (ROOT/"database/seeds/20261126_plantillas_complementarias_piloto.sql").read_text(encoding="utf-8")
    with db.connect(autocommit=True) as c:
        anteriores = c.execute("SELECT to_jsonb(p) FROM plantillas p ORDER BY id").fetchall()
        for _ in range(2):
            c.execute(archivo)
        actuales = c.execute("SELECT to_jsonb(p) FROM plantillas p ORDER BY id").fetchall()
        assert all(fila in actuales for fila in anteriores)
        assert len(actuales) == len(anteriores)+2
        assert c.execute("SELECT count(*) FROM campos_plantilla WHERE plantilla_id IN (SELECT id FROM plantillas WHERE nombre IN ('Informe Legal – Piloto NAXJI','Memorando – Piloto NAXJI'))").fetchone()[0] == 6
