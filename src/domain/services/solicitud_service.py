from datetime import date
from math import isfinite
from typing import Any

from src.domain.entities.plantilla import CampoPlantilla, Plantilla
from src.domain.entities.solicitud import Solicitud
from src.domain.services.errores import ConflictoEstado, DatosInvalidos
from src.domain.value_objects.estado_solicitud import EstadoSolicitud
from src.domain.value_objects.estados import TipoDato


class SolicitudService:

    @staticmethod
    def validar(solicitud: Solicitud) -> None:
        if not isinstance(solicitud.asunto, str) or not solicitud.asunto.strip():
            raise DatosInvalidos("El asunto es obligatorio")

    @staticmethod
    def editable(solicitud: Solicitud) -> None:
        if solicitud.estado not in (EstadoSolicitud.BORRADOR, EstadoSolicitud.LISTA_PARA_GENERAR):
            raise ConflictoEstado("La solicitud ya no admite modificaciones")

    @staticmethod
    def validar_valor(campo: CampoPlantilla, valor: Any) -> None:
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise DatosInvalidos(f"El valor de {campo.clave} no puede estar vacío")
        tipo = campo.tipo_dato
        correcto = True
        if tipo in (TipoDato.TEXT, TipoDato.TEXTAREA):
            correcto = isinstance(valor, str)
        elif tipo == TipoDato.BOOLEAN:
            correcto = type(valor) is bool
        elif tipo == TipoDato.NUMBER:
            correcto = type(valor) in (int, float) and isfinite(valor)
        elif tipo == TipoDato.DATE:
            try:
                correcto = isinstance(valor, str) and date.fromisoformat(valor).isoformat() == valor
            except ValueError:
                correcto = False
        elif tipo == TipoDato.SELECT:
            opciones = campo.configuracion.get("opciones", [])
            correcto = isinstance(valor, str) and valor in opciones
        if not correcto:
            raise DatosInvalidos(f"Valor incompatible con el campo {campo.clave} ({tipo.value})")

    @staticmethod
    def validar_obligatorios(solicitud: Solicitud, plantilla: Plantilla) -> None:
        valores = {v.campo_plantilla_id: v.valor for v in solicitud.valores}
        campos = {c.id: c for c in plantilla.campos if c.activo}
        if valores.keys() - campos.keys():
            raise DatosInvalidos("Existen valores ajenos a la plantilla activa")
        for campo in campos.values():
            if campo.obligatorio and campo.id not in valores:
                raise DatosInvalidos(f"Falta el campo obligatorio: {campo.clave}")
            if campo.id in valores:
                SolicitudService.validar_valor(campo, valores[campo.id])
