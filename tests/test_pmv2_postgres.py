"""Base nueva en loopback únicamente. Nunca usa .env ni Supabase compartido."""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from io import BytesIO
import json
import os
from pathlib import Path
from uuid import UUID, uuid4

from docx import Document
from fastapi.testclient import TestClient
import pytest

from src.adapters.out.ai.context_predictor_mock import ContextPredictorMock
from src.adapters.out.ai.embeddings_ollama import EmbeddingsOllama
from src.adapters.out.ai.generador_borrador_mock import GeneradorBorradorMock
from src.adapters.out.persistence.documentos_postgres import DocumentosPostgres
from src.adapters.out.persistence.postgres import PostgresUnidadTrabajo, InformeRepositoryPostgres
from src.adapters.out.documents.extractor import ExtractorArchivos
from src.application.use_cases.documentos import GestionDocumentos
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.entities.solicitud import ahora
from src.domain.services.errores import ConflictoEstado, NoEncontrado
from src.domain.value_objects.estados import Rol
from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings
from src.infrastructure.configuration.rag import RagSettings
from src.infrastructure.dependencies import get_current_user
from src.main import create_app
from tests.pmv2_dobles import AlmacenMemoria, EmbeddingsPrueba
from tests.test_estructura_postgres import db_local, script  # noqa: F401
from tests.test_piloto_v2 import preparar_v2
from tests.test_pmv2 import cargar


pytestmark = pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL + pgvector aislado: opt-in")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def pmv2_db(db_local):
    settings, uid, pid, iid, contenido = db_local
    with settings.connect() as c:
        antes = c.execute("SELECT to_jsonb(v) FROM public.versiones_informe v ORDER BY id").fetchall()
        for _ in range(2):
            script(c, "database/migrations/20261030_01_documentos_rag.sql")
            assert c.execute("SELECT to_jsonb(v)-'sustento' FROM public.versiones_informe v ORDER BY id").fetchall() == antes
        assert c.execute("SELECT count(*) FROM public.documentos").fetchone()[0] == 0
        assert c.execute("SELECT count(*) FROM pg_class WHERE relname IN ('documentos','documento_fragmentos','version_citas') AND relrowsecurity").fetchone()[0] == 3
    uow = PostgresUnidadTrabajo(settings)
    gestor = GestionDocumentos(DocumentosPostgres(uow), AlmacenMemoria(), ExtractorArchivos(), EmbeddingsPrueba(), RagSettings())
    deps = Container(Settings(persistence_mode="postgres", auth_mode="disabled"), database_settings=settings,
                     predictor=ContextPredictorMock(), generador=GeneradorBorradorMock(), documentos=gestor)
    usuario = UsuarioActual(uid, frozenset({Rol.FUNCIONARIO}), deps.catalogos.areas()[0].id)
    yield settings, gestor, deps, usuario, iid


def test_sql_preserva_primera_repeticion_persistencia_y_filtros(pmv2_db):
    settings, gestor, deps, usuario, iid = pmv2_db
    doc = cargar(gestor, usuario)
    assert cargar(gestor, usuario).id == doc.id
    gestor.procesar(doc.id, usuario)
    otro_repo = DocumentosPostgres(PostgresUnidadTrabajo(settings))
    assert otro_repo.obtener(doc.id).estado == "INDEXADO"
    resultados = gestor.recuperar("parque", usuario)
    assert resultados["estado"] == "RECUPERADO"
    ajeno = replace(usuario, id=uuid4(), area_id=uuid4())
    assert gestor.recuperar("parque", ajeno)["estado"] == "CORPUS_VACIO"
    with pytest.raises(NoEncontrado): gestor.obtener(doc.id, ajeno)
    area = cargar(gestor, usuario, ambito="AREA"); gestor.procesar(area.id, usuario)
    par = replace(ajeno, area_id=usuario.area_id)
    assert [d.id for d in gestor.listar(par)] == [area.id]
    assert {r["documento_id"] for r in gestor.recuperar("parque", par)["fuentes"]} == {str(area.id)}
    assert gestor.recuperar("impuestos", usuario)["estado"] == "SIN_RESULTADOS"
    anterior = deepcopy(deps.informes.obtener_por_id(iid))
    gestor.procesamiento += ":revision2"; gestor.procesar(doc.id, usuario)
    with settings.connect() as c:
        assert c.execute("SELECT count(*),min(vector_dims(embedding)) FROM public.documento_fragmentos WHERE documento_id=%s", (doc.id,)).fetchone() == (1, 1024)
        script(c, "database/checks/20261030_verificar_pmv2.sql")
    assert deps.informes.obtener_por_id(iid) == anterior


def test_pg_citas_versiones_edicion_recuperacion_atomica(pmv2_db):
    from dataclasses import replace
    from unittest.mock import Mock
    settings, gestor, deps, usuario, _ = pmv2_db
    doc = cargar(gestor, usuario); gestor.procesar(doc.id, usuario)
    original = deps.generar_borrador.generador.generar
    def generar(*args):
        assert not deps.uow.active and not gestor.repo.uow.active
        resultado = original(*args)
        fid = args[3].fuentes[0]["fragmento_id"]
        return replace(resultado, contenido={k: v + f" [F:{fid}]" for k, v in resultado.contenido.items()})
    deps.generar_borrador.generador = Mock(generar=generar)
    from src.application.ports.input.solicitud_use_case import DatosSolicitud
    from src.domain.value_objects.estados import ResultadoValidacion
    s = deps.crear_solicitud.ejecutar(usuario, DatosSolicitud("Inspección de parque"))
    p = deps.predecir_contexto.ejecutar(s.id, usuario)
    plantilla = next(p for p in deps.plantillas.listar() if p.nombre == "Informe Técnico – Piloto NAXJI")
    deps.validar_prediccion.ejecutar(s.id, usuario, p.id, ResultadoValidacion.CORREGIDA,
                                    plantilla.tipo_informe_id, usuario.area_id, [])
    deps.actualizar_solicitud.ejecutar(s.id, usuario, {"plantilla_id": plantilla.id})
    deps.guardar_valores.ejecutar(s.id, usuario, {c.id: ("2026-10-30" if c.tipo_dato.value == "date" else "Datos para " + c.clave)
                                                for c in plantilla.campos if c.obligatorio})
    informe = deps.generar_borrador.ejecutar(s.id, usuario, usar_documentos=True)
    snapshot = deepcopy(informe.versiones[0].sustento)
    assert InformeRepositoryPostgres(PostgresUnidadTrabajo(settings)).obtener_por_id(informe.id).versiones[0].sustento == snapshot
    contenido = {**informe.versiones[0].contenido, "antecedentes": "Edición del funcionario"}
    deps.actualizar_borrador.ejecutar(informe.id, usuario, contenido, 1)
    with settings.connect() as c:
        assert c.execute("SELECT count(*) FROM public.version_citas WHERE version_id=%s", (informe.versiones[0].id,)).fetchone()[0] == len(informe.versiones[0].sustento["fuentes"][0]["citas"])
        assert c.execute("SELECT count(*) FROM public.version_citas WHERE estado='TEXTO_MODIFICADO'").fetchone()[0] == 1
    gestor.procesamiento += ":reindexar"; gestor.procesar(doc.id, usuario)
    assert deps.obtener_informe.ejecutar(informe.id, usuario).versiones[0].sustento == snapshot
    gestor.embeddings.fallar = True
    assert deps.exportar_informe.ejecutar(informe.id, 1, usuario).startswith(b"PK")


def test_pg_reservas_no_permiten_resultado_tardio(pmv2_db):
    _, gestor, _, usuario, _ = pmv2_db
    doc = cargar(gestor, usuario)
    intento = uuid4()
    gestor.repo.reservar(doc.id, "PROCESANDO", intento, ahora() + timedelta(minutes=1))
    with pytest.raises(ConflictoEstado):
        gestor.repo.reservar(doc.id, "PROCESANDO", uuid4(), ahora() + timedelta(minutes=1))
    with pytest.raises(ConflictoEstado):
        gestor.repo.finalizar(doc.id, uuid4(), "INDEXADO", fragmentos=[])
    assert gestor.obtener(doc.id, usuario).intento == intento


def test_pgvector_instalado_en_extensions_conserva_esquema(db_local):
    settings, uid, _, _, _ = db_local
    with settings.connect() as c:
        c.execute("CREATE SCHEMA extensions; CREATE EXTENSION vector WITH SCHEMA extensions")
        script(c, "database/migrations/20261030_01_documentos_rag.sql")
    gestor = GestionDocumentos(DocumentosPostgres(PostgresUnidadTrabajo(settings)), AlmacenMemoria(),
                               ExtractorArchivos(), EmbeddingsPrueba(), RagSettings())
    usuario = UsuarioActual(uid, frozenset({Rol.FUNCIONARIO}))
    doc = cargar(gestor, usuario); gestor.procesar(doc.id, usuario)
    assert gestor.recuperar("parque", usuario)["estado"] == "RECUPERADO"


@pytest.mark.skipif(os.getenv("NAXJI_RUN_PMV2_AI_TESTS") != "1", reason="Embeddings y Ollama reales: opt-in")
def test_pmv2_pgvector_embeddings_y_ollama_reales(pmv2_db):
    settings, gestor, _, usuario, _ = pmv2_db
    gestor.embeddings = EmbeddingsOllama("http://localhost:11434")
    gestor.procesamiento = f"extract-v1:chars-v1:1200:180:{gestor.embeddings.modelo}:1024:1"
    with settings.connect() as c:
        script(c, "database/seeds/20261001_piloto_v2_datos_fuente.sql")
    config = Settings(persistence_mode="postgres", auth_mode="disabled", ollama_timeout_seconds=300)
    deps = Container(config, database_settings=settings, predictor=ContextPredictorMock(), documentos=gestor)
    app = create_app(config, deps)
    app.dependency_overrides[get_current_user] = lambda: usuario
    evidencia = {"tipo": "PostgreSQL+pgvector, embeddings y Ollama reales; Storage y Auth con dobles",
                 "corpus": "SINTETICO-PMV2-REAL-01", "modelo_embeddings": gestor.embeddings.modelo, "dimension": 1024}
    with TestClient(app) as client:
        cargado = client.post("/documentos", files={"archivo": ("manual.txt", (
            "Documento ficticio de pruebas. Guía de gestión ambiental para parques. "
            "Para valorar residuos en un parque se necesitan observaciones documentadas y ubicación precisa. "
            "Esta guía no registra inspecciones ni hallazgos de ningún expediente.").encode(), "text/plain")},
            data={"titulo": "Guía ambiental ficticia PMV2", "procedencia": "Corpus sintético autorizado para pruebas", "ambito": "PRIVADO"})
        assert cargado.status_code == 201, cargado.text
        did = cargado.json()["id"]
        assert client.post(f"/documentos/{did}/procesar").status_code == 200
        recuperado = client.post("/documentos/recuperar", json={"consulta": "Gestión ambiental e inspección de parque"})
        assert recuperado.json()["estado"] == "RECUPERADO", recuperado.text
        sid, _ = preparar_v2(client, asunto="Elaborar informe sobre criterios para documentar una inspección ambiental de parque")
        intentos = []
        for _ in range(2):
            generado = client.post(f"/solicitudes/{sid}/generar-borrador", json={"usar_documentos": True})
            intentos.append({"status": generado.status_code, "respuesta": generado.json()})
            if generado.status_code == 201:
                break
        evidencia["intentos"] = intentos
        ruta = os.getenv("NAXJI_PMV2_EVIDENCE_DIR")
        if ruta:
            destino = Path(ruta); destino.mkdir(parents=True, exist_ok=True)
            (destino / "ollama-real.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")


        assert generado.status_code == 201, generado.text
        informe = generado.json(); iid = informe["informe_id"]
        assert informe["sustento"]["estado"] == "RECUPERADO"
        assert any(f["citas"] for f in informe["sustento"]["fuentes"]), "El modelo recuperó fuentes pero no citó ninguna"
        contenido = {**informe["contenido"], "conclusiones": "Pendiente de verificación: edición humana ficticia; faltan resultados."}
        editado = client.put(f"/informes/{iid}", json={"contenido": contenido, "numero_version": 1})
        assert editado.status_code == 200
        deps.generar_borrador.generador = None
        assert client.get(f"/informes/{iid}/versiones/1").json()["sustento"] == informe["sustento"]
        assert client.get(f"/informes/{iid}/versiones/2").json()["contenido"] == contenido
        descargado = client.get(f"/informes/{iid}/versiones/2/docx")
        assert descargado.status_code == 200
        assert "Guía ambiental ficticia" in "\n".join(p.text for p in Document(BytesIO(descargado.content)).paragraphs)
        evidencia["recorrido"] = {"carga": 201, "procesamiento": 200, "generacion": 201,
                                  "edicion": 200, "recuperacion": 200, "docx": 200}
        evidencia["version_editada"] = editado.json()
        if ruta:
            (destino / "ollama-real.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")


@pytest.mark.skipif(os.getenv("NAXJI_RUN_PMV2_AI_TESTS") != "1", reason="Embeddings reales y pgvector: opt-in")
def test_evaluacion_recuperacion_pgvector_real(pmv2_db):
    from hashlib import sha256
    settings, gestor, _, usuario, _ = pmv2_db
    gestor.embeddings = EmbeddingsOllama("http://localhost:11434")
    gestor.procesamiento = "eval-pmv2:bge-m3:567m:1024:v1"
    archivo = ROOT / "tests/fixtures/pmv2_corpus.json"
    corpus = json.loads(archivo.read_text(encoding="utf-8"))
    mapa = {}
    for referencia in corpus["documentos"]:
        doc = gestor.cargar(usuario, referencia["id"] + ".txt", referencia["texto"].encode(),
                            referencia["titulo"], corpus["id"], "PRIVADO")
        gestor.procesar(doc.id, usuario)
        mapa[str(doc.id)] = referencia["id"]
    resultados = []
    for consulta in corpus["consultas"]:
        respuesta = gestor.recuperar(consulta["texto"], usuario)
        encontrados = [mapa[f["documento_id"]] for f in respuesta["fuentes"]]
        relevantes = set(consulta["relevantes"])
        aciertos = len(relevantes.intersection(encontrados))
        resultados.append({"id": consulta["id"], "estado": respuesta["estado"], "relevantes": sorted(relevantes),
                           "encontrados": encontrados, "similitudes": [f["similitud"] for f in respuesta["fuentes"]],
                           "precision": aciertos/len(encontrados) if encontrados else 0,
                           "recall": aciertos/len(relevantes) if relevantes else None})
    positivas = [r for r in resultados if r["relevantes"]]
    negativas = [r for r in resultados if not r["relevantes"]]
    evidencia = {"tipo": "Adaptador de recuperación PostgreSQL+pgvector y bge-m3 reales; corpus sintético",
                 "corpus": corpus["id"], "sha256": sha256(archivo.read_bytes()).hexdigest(), "umbral_similitud": gestor.config.threshold,
                 "top_k": gestor.config.top_k, "dimension": 1024, "resultados": resultados,
                 "macro_precision_at_k": sum(r["precision"] for r in positivas)/len(positivas),
                 "macro_recall_at_k": sum(r["recall"] for r in positivas)/len(positivas),
                 "rechazo_negativas": sum(not r["encontrados"] for r in negativas)/len(negativas),
                 "revision_humana_institucional": "Pendiente; no inferir calidad general a partir de este corpus"}
    with settings.connect() as c:
        evidencia["pgvector_version"] = c.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()[0]
    ruta = os.getenv("NAXJI_PMV2_EVIDENCE_DIR")
    if ruta:
        destino = Path(ruta); destino.mkdir(parents=True, exist_ok=True)
        (destino / "recuperacion-pgvector-real.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")
    assert evidencia["macro_recall_at_k"] == 1 and evidencia["rechazo_negativas"] == 1
