"""Fixtures ficticias en memoria. No son registros ni UUID de Supabase."""
from uuid import NAMESPACE_URL, uuid5

from src.domain.entities.catalogo import AreaMunicipal, Normativa, TipoInforme
from src.domain.entities.plantilla import CampoPlantilla, Plantilla
from src.domain.value_objects.estados import TipoDato


def demo_id(nombre: str):
    return uuid5(NAMESPACE_URL, f"naxji:demo:{nombre}")


TIPOS = [TipoInforme(demo_id(codigo), codigo, nombre) for codigo, nombre in (
    ("INFORME_TECNICO", "Informe Técnico"),
    ("INFORME_LEGAL", "Informe Legal"),
    ("INFORME_INSPECCION", "Informe de Inspección"),
    ("MEMORANDO", "Memorando"),
)]
AREAS = [AreaMunicipal(demo_id("AREA_ECOLOGIA"), "AREA_ECOLOGIA",
                       "Ecología y Medio Ambiente (DEMO)"),
         AreaMunicipal(demo_id("AREA_ADMINISTRACION"), "AREA_ADMINISTRACION",
                       "Administración (DEMO)")]
NORMATIVA = Normativa(demo_id("NORMA_DEMO"), "NORMA_DEMO",
                      "Normativa ficticia para pruebas; sin valor legal")


def plantillas_demo() -> list[Plantilla]:
    resultado = []
    for tipo in TIPOS:
        plantilla = Plantilla(demo_id(f"plantilla:{tipo.codigo}"),
                              f"{tipo.nombre} (DEMO)", tipo.id)
        for orden, (clave, dato, obligatorio, config) in enumerate((
            ("antecedentes", TipoDato.TEXTAREA, True, {}),
            ("detalle", TipoDato.TEXT, True, {}),
            ("fecha", TipoDato.DATE, False, {}),
            ("cantidad", TipoDato.NUMBER, False, {}),
            ("verificado", TipoDato.BOOLEAN, False, {}),
            ("prioridad", TipoDato.SELECT, False, {"opciones": ["NORMAL", "ALTA"]}),
        ), start=1):
            plantilla.campos.append(CampoPlantilla(
                demo_id(f"{tipo.codigo}:{clave}"), plantilla.id, clave,
                clave.capitalize(), dato, obligatorio, orden, config,
            ))
        resultado.append(plantilla)
    return resultado
