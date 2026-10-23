"""Regresiones de la evaluación formativa; PostgreSQL solo en clúster desechable."""
from dataclasses import replace
import os
from unittest.mock import Mock
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb
import pytest

from src.adapters.out.ai.sklearn_context_predictor import SklearnContextPredictor
from src.domain.entities.plantilla import CampoPlantilla
from src.domain.services.solicitud_service import SolicitudService
from src.domain.value_objects.estados import TipoDato
from src.domain.value_objects.seccion_salida import secciones_desde_json
from src.domain.services.errores import DatosInvalidos
from tests.test_estructura_postgres import db_local, script  # noqa: F401


@pytest.mark.parametrize("tipo_existente", [True, False])
@pytest.mark.parametrize("operacion", ["crear", "actualizar"])
def test_tipo_inferido_de_plantilla_debe_existir_y_estar_activo(client, deps, tipo_existente, operacion):
    plantilla = deps.plantillas.listar()[0]
    tipos = deps.catalogos.tipos_informe()
    deps.catalogos.tipos_informe = Mock(return_value=[
        replace(t, activo=False) if t.id == plantilla.tipo_informe_id else t
        for t in tipos if tipo_existente or t.id != plantilla.tipo_informe_id
    ])
    body = {"asunto": "Solicitud de prueba", "plantilla_id": str(plantilla.id),
            "area_destino_id": str(plantilla.area_id) if plantilla.area_id else None}
    if operacion == "crear":
        respuesta = client.post("/solicitudes", json=body)
        assert not deps.memoria.solicitudes
    else:
        creada = client.post("/solicitudes", json={"asunto": "Original"}).json()
        respuesta = client.put("/solicitudes/" + creada["id"], json=body)
        assert client.get("/solicitudes/" + creada["id"]).json() == creada
    assert respuesta.status_code == 404, respuesta.text


def test_tipo_inferido_activo_sigue_funcionando(client):
    plantilla = client.get("/plantillas").json()[0]
    respuesta = client.post("/solicitudes", json={
        "asunto": "Solicitud válida", "plantilla_id": plantilla["id"],
        "area_destino_id": plantilla["area_id"],
    })
    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["tipo_informe_id"] == plantilla["tipo_informe_id"]


def test_entero_grande_es_finito_y_se_integra_por_rest(client, deps):
    plantilla = deps.plantillas.listar()[0]
    campo = CampoPlantilla(uuid4(), plantilla.id, "numero", "Número", TipoDato.NUMBER, True, 1)
    plantilla.campos = [campo]
    deps.plantillas.obtener_por_id = Mock(return_value=plantilla)
    valor = 10 ** 400
    SolicitudService.validar_valor(campo, valor)
    r = client.post("/solicitudes", json={"asunto": "Número de prueba", "plantilla_id": str(plantilla.id),
                                         "area_destino_id": str(plantilla.area_id) if plantilla.area_id else None})
    assert r.status_code == 201, r.text
    url = "/solicitudes/" + r.json()["id"]
    r = client.put(url + "/valores", json={"valores": [{"campo_plantilla_id": str(campo.id), "valor": valor}]})
    assert r.status_code == 200, r.text
    assert client.get(url).json()["valores"][0]["valor"] == valor


def test_metadatos_describen_estimadores_reales_y_no_precision(client, deps):
    predictor = SklearnContextPredictor()
    assert predictor.algoritmos == {
        "tipo_informe": "LogisticRegression", "area_destino": "LogisticRegression",
        "normativas": "OneVsRestClassifier[LogisticRegression]",
    }
    deps.predecir_contexto.predictor = predictor
    r = client.post("/solicitudes", json={"asunto": "Inspección de parque municipal"})
    r = client.post("/solicitudes/" + r.json()["id"] + "/predecir-contexto")
    assert r.status_code == 200, r.text
    assert r.json()["modelo"] == "SKLEARN_IA_01"
    assert r.json()["algoritmos"] == predictor.algoritmos
    # Es la identificación histórica del artefacto, no un resultado experimental.
    assert r.json()["version_modelo"] == "RF-IA-01-200CASOS-v1"
    assert not r.json()["es_mock"]


@pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL local aislado: opt-in")
def test_funcion_sql_rechaza_titulos_vacios_segun_el_dominio(db_local):
    settings, _, pid, _, _ = db_local
    # Todos los caracteres considerados espacio por str.strip(), sin depender
    # de la definición POSIX/locale de PostgreSQL.
    espacios = [chr(c) for c in range(0x3100) if chr(c).isspace()]
    with settings.connect(autocommit=True) as c:
        antes = c.execute("SELECT to_jsonb(p) FROM public.plantillas p ORDER BY id").fetchall()
        for _ in range(2):
            script(c, "database/migrations/20261023_01_validar_titulos_secciones.sql")
        assert c.execute("SELECT to_jsonb(p) FROM public.plantillas p ORDER BY id").fetchall() == antes
        assert c.execute("SELECT public.naxji_secciones_salida_validas(NULL)").fetchone()[0] is True
        for titulo in espacios + ["".join(espacios)]:
            valor = [{"clave": "resumen", "titulo": titulo, "obligatoria": True}]
            with pytest.raises(DatosInvalidos):
                secciones_desde_json(valor)
            assert c.execute("SELECT public.naxji_secciones_salida_validas(%s)", (Jsonb(valor),)).fetchone()[0] is False
            with pytest.raises(psycopg.errors.CheckViolation):
                c.execute("UPDATE public.plantillas SET secciones_salida=%s WHERE id=%s", (Jsonb(valor), pid))
            with pytest.raises(psycopg.errors.CheckViolation):
                c.execute("UPDATE public.versiones_informe SET secciones_salida=%s", (Jsonb(valor),))
        valor = [{"clave": "resumen", "titulo": "\tResumen válido\n", "obligatoria": True}]
        assert secciones_desde_json(valor)[0].titulo == valor[0]["titulo"]
        assert c.execute("SELECT public.naxji_secciones_salida_validas(%s)", (Jsonb(valor),)).fetchone()[0] is True


@pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL local aislado: opt-in")
def test_migracion_revierte_si_una_fila_anterior_tiene_titulo_invalido(db_local):
    settings, _, pid, _, _ = db_local
    valor = [{"clave": "resumen", "titulo": "\t", "obligatoria": True}]
    with settings.connect(autocommit=True) as c:
        # La función anterior permite esta fila. La corrección debe detectarla
        # sin reescribir datos ni dejar una migración aplicada parcialmente.
        c.execute("UPDATE public.plantillas SET secciones_salida=%s WHERE id=%s", (Jsonb(valor), pid))
        with pytest.raises(psycopg.errors.CheckViolation):
            script(c, "database/migrations/20261023_01_validar_titulos_secciones.sql")
        c.rollback()
        assert c.execute("SELECT secciones_salida FROM public.plantillas WHERE id=%s", (pid,)).fetchone()[0] == valor
        assert c.execute("SELECT public.naxji_secciones_salida_validas(%s)", (Jsonb(valor),)).fetchone()[0] is True
        assert c.execute("SELECT convalidated FROM pg_constraint WHERE conname='chk_plantilla_secciones_salida'").fetchone()[0] is True


@pytest.mark.skipif(not os.getenv("NAXJI_TEST_PG_PORT"), reason="PostgreSQL local aislado: opt-in")
def test_funciones_y_trigger_auth_existentes_en_postgres_desechable(db_local):
    settings, uid, _, _, _ = db_local
    with settings.connect(autocommit=True) as c:
        # Dobles mínimos del esquema/proveedor Supabase; NO validan Auth real.
        c.execute("""DO $$ BEGIN
          IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='anon') THEN CREATE ROLE anon; END IF;
          IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='authenticated') THEN CREATE ROLE authenticated; END IF;
        END $$;
        ALTER TABLE auth.users ADD COLUMN raw_user_meta_data jsonb DEFAULT '{}';
        CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $$
          SELECT nullif(current_setting('request.jwt.claim.sub',true),'')::uuid
        $$;
        GRANT USAGE ON SCHEMA auth TO authenticated;
        GRANT EXECUTE ON FUNCTION auth.uid() TO authenticated;""")
        for _ in range(2):
            script(c, "migrations/20260928_01_auth_rls.sql")
        c.execute("INSERT INTO public.usuario_roles(usuario_id,rol_id) SELECT %s,id FROM public.roles WHERE codigo='FUNCIONARIO'", (uid,))
        nuevo = uuid4()
        c.execute("INSERT INTO auth.users(id,raw_user_meta_data) VALUES (%s,%s)",
                  (nuevo, Jsonb({"nombres": "Prueba", "roles": ["ADMINISTRADOR"], "activo": True})))
        assert c.execute("SELECT activo FROM public.perfiles WHERE id=%s", (nuevo,)).fetchone()[0] is False
        assert c.execute("SELECT count(*) FROM public.usuario_roles WHERE usuario_id=%s", (nuevo,)).fetchone()[0] == 0
        c.execute("SELECT set_config('request.jwt.claim.sub',%s,false)", (str(uid),))
        c.execute("SET ROLE authenticated")
        assert c.execute("SELECT naxji_private.has_role(ARRAY['FUNCIONARIO']),naxji_private.can_read()").fetchone() == (True, True)
        assert c.execute("SELECT count(*) FROM public.perfiles").fetchone()[0] == 1
        assert c.execute("SELECT has_function_privilege(current_user,'naxji_private.create_pending_profile()','EXECUTE')").fetchone()[0] is False
        c.execute("RESET ROLE")
        c.execute("SELECT set_config('request.jwt.claim.sub',%s,false)", (str(nuevo),))
        c.execute("SET ROLE authenticated")
        assert c.execute("SELECT naxji_private.can_read()").fetchone()[0] is False
        assert c.execute("SELECT count(*) FROM public.perfiles").fetchone()[0] == 0
        c.execute("RESET ROLE")
