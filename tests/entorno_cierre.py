"""Entorno desechable de laboratorio. Nunca compone Auth/Storage dobles en producción."""
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException, Request
from psycopg import sql

from src.infrastructure.configuration.database import DatabaseSettings
from src.infrastructure.configuration.container import Container
from src.infrastructure.configuration.settings import Settings
from src.infrastructure.configuration.rag import RagSettings
from src.infrastructure.dependencies import get_current_user
from src.domain.entities.usuario_actual import UsuarioActual
from src.domain.value_objects.estados import Rol, ResultadoValidacion
from src.application.ports.input.solicitud_use_case import DatosSolicitud
from src.adapters.out.persistence.documentos_postgres import DocumentosPostgres
from src.adapters.out.persistence.postgres import PostgresUnidadTrabajo
from src.adapters.out.documents.extractor import ExtractorArchivos
from src.adapters.out.ai.generador_borrador_mock import GeneradorBorradorMock
from src.application.use_cases.documentos import GestionDocumentos
from src.main import create_app
from tests.pmv2_dobles import AlmacenMemoria, EmbeddingsPrueba

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def entorno_aislado(puerto):
    # Destino fijo loopback, rol específico de pruebas, nombre aleatorio recién creado.
    admin = DatabaseSettings("127.0.0.1", puerto, "postgres", "naxji_step3", "", sslmode="disable")
    nombre = "naxji_cierre_" + uuid4().hex
    with admin.connect(autocommit=True) as c:
        c.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(sql.Identifier(nombre)))
    db = replace(admin, dbname=nombre)
    try:
        with db.connect(autocommit=True) as c:
            c.execute("CREATE SCHEMA auth; CREATE TABLE auth.users(id uuid PRIMARY KEY)")
            c.execute((ROOT / "NAXJI_database_schema_actual.sql").read_text(encoding="utf-8-sig"))
            c.execute((ROOT / "database/seeds/pmv1_catalogos.sql").read_text(encoding="utf-8-sig"))
            for migracion in sorted((ROOT / "database/migrations").glob("*.sql")):
                c.execute(migracion.read_text(encoding="utf-8-sig"))
            for semilla in ("paso3_estructura_piloto.sql", "20261001_piloto_v2_datos_fuente.sql", "20261126_plantillas_complementarias_piloto.sql"):
                c.execute((ROOT / "database/seeds" / semilla).read_text(encoding="utf-8-sig"))
            area = c.execute("SELECT id FROM areas_municipales WHERE codigo='MDT_SGGA'").fetchone()[0]
            usuarios = {}
            for nombre_rol, rol in (("autor", Rol.FUNCIONARIO), ("revisor", Rol.REVISOR), ("admin", Rol.ADMINISTRADOR), ("otro", Rol.FUNCIONARIO)):
                uid = uuid4()
                c.execute("INSERT INTO auth.users VALUES (%s)", (uid,))
                c.execute("INSERT INTO perfiles(id,nombres,apellidos) VALUES (%s,'Prueba','Sintetica')", (uid,))
                usuarios[nombre_rol] = UsuarioActual(uid, frozenset({rol}), area)
        config = Settings(persistence_mode="postgres", auth_mode="disabled", pmv3_enabled=True)
        rag = RagSettings()
        gestor = GestionDocumentos(DocumentosPostgres(PostgresUnidadTrabajo(db)), AlmacenMemoria(),
                                   ExtractorArchivos(), EmbeddingsPrueba(), rag)
        deps = Container(config, database_settings=db, generador=GeneradorBorradorMock(), documentos=gestor)
        app = create_app(config, deps)
        def identidad_prueba(request: Request):
            identidad = request.headers.get("Authorization", "").removeprefix("Bearer laboratorio-")
            if identidad not in usuarios:
                raise HTTPException(401, "Identidad de laboratorio inválida")
            return usuarios[identidad]
        app.dependency_overrides[get_current_user] = identidad_prueba
        yield SimpleNamespace(app=app, deps=deps, db=db, usuarios=usuarios, area=area)
    finally:
        with admin.connect(autocommit=True) as c:
            c.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(nombre)))


def solicitud_lista(entorno, numero):
    d, autor = entorno.deps, entorno.usuarios["autor"]
    asunto = f"Caso ficticio {numero}: documentar criterios ambientales para residuos de un parque, sin inspección acreditada"
    s = d.crear_solicitud.ejecutar(autor, DatosSolicitud(asunto))
    p = d.predecir_contexto.ejecutar(s.id, autor)
    plantilla = next(p for p in d.plantillas.listar() if p.version == 2 and "Piloto NAXJI" in p.nombre)
    d.validar_prediccion.ejecutar(s.id, autor, p.id, ResultadoValidacion.CORREGIDA,
                                plantilla.tipo_informe_id, entorno.area, [])
    d.actualizar_solicitud.ejecutar(s.id, autor, {"plantilla_id": plantilla.id, "area_origen_id": entorno.area})
    d.guardar_valores.ejecutar(s.id, autor, {c.id: "Sin resultados de inspección" for c in plantilla.campos if c.obligatorio})
    return s.id
