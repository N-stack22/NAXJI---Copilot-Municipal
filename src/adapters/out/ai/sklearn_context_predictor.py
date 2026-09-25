import json
from pathlib import Path
from uuid import UUID, NAMESPACE_URL, uuid5

import numpy as np
from joblib import load

from src.application.ports.output.context_predictor import ContextPredictor
from src.domain.entities.prediccion_contexto import (
    NormativaPredicha,
    PrediccionContexto,
)


# ============================================================
# Conversión de las etiquetas que devuelve el modelo
# a códigos temporales del catálogo demo del backend.
# ============================================================

TIPOS = {
    "Informe Técnico": "INFORME_TECNICO",
    "Informe Legal": "INFORME_LEGAL",
    "Informe de Inspección": "INFORME_INSPECCION",
    "Memorando": "MEMORANDO",
}


AREAS = {
    "Subgerencia de Ecología y Medio Ambiente": "AREA_ECOLOGIA",
    "Gerencia de Servicios Públicos": "AREA_SERVICIOS_PUBLICOS",
    "Gerencia de Desarrollo Urbano": "AREA_DESARROLLO_URBANO",
    "Gerencia de Desarrollo Económico": "AREA_DESARROLLO_ECONOMICO",
    "Subgerencia de Gestión del Riesgo de Desastres": "AREA_RIESGO_DESASTRES",
    "Oficina de Asesoría Jurídica": "AREA_ASESORIA_JURIDICA",
}


def demo_id(nombre: str) -> UUID:
    """
    Genera los mismos UUID determinísticos utilizados
    por los datos demo del backend.
    """
    return uuid5(
        NAMESPACE_URL,
        f"naxji:demo:{nombre}"
    )


class SklearnContextPredictor(ContextPredictor):

    def __init__(self):

        # sklearn_context_predictor.py está en:
        # src/adapters/out/ai/
        #
        # Los modelos están en:
        # src/infrastructure/ai/models/

        src_path = Path(__file__).resolve().parents[3]

        models_path = (
            src_path
            / "infrastructure"
            / "ai"
            / "models"
        )

        self.modelo_tipo = load(
            models_path / "modelo_tipo.joblib"
        )

        self.modelo_area = load(
            models_path / "modelo_area.joblib"
        )

        self.features_norm = load(
            models_path / "features_norm.joblib"
        )

        self.modelo_normas = load(
            models_path / "modelo_normas.joblib"
        )

        self.mlb = load(
            models_path / "mlb.joblib"
        )

        with open(
            models_path / "model_config.json",
            "r",
            encoding="utf-8",
        ) as archivo:
            self.config = json.load(archivo)

        self.umbral_normas = float(
            self.config.get(
                "umbral_normas",
                0.50
            )
        )

        self.version_modelo = self.config.get(
            "version_modelo",
            "RF-IA-01-v1"
        )

    # --------------------------------------------------------
    # Obtener probabilidad de la clase elegida
    # --------------------------------------------------------

    @staticmethod
    def _confianza_clase(
        modelo,
        texto: str,
        clase_predicha: str,
    ) -> float | None:

        if not hasattr(
            modelo,
            "predict_proba"
        ):
            return None

        probabilidades = modelo.predict_proba(
            [texto]
        )[0]

        clases = modelo.classes_

        for indice, clase in enumerate(clases):
            if str(clase) == str(clase_predicha):
                return float(
                    probabilidades[indice]
                )

        return None

    # --------------------------------------------------------
    # Predicción principal
    # --------------------------------------------------------

    def predecir(
        self,
        asunto: str,
        solicitud_id: UUID,
    ) -> PrediccionContexto:

        # ============================
        # 1. TIPO DE INFORME
        # ============================

        tipo_nombre = str(
            self.modelo_tipo.predict(
                [asunto]
            )[0]
        )

        if tipo_nombre not in TIPOS:
            raise ValueError(
                f"Tipo de informe desconocido "
                f"devuelto por el modelo: "
                f"{tipo_nombre}"
            )

        tipo_codigo = TIPOS[tipo_nombre]

        tipo_id = demo_id(
            tipo_codigo
        )

        confianza_tipo = (
            self._confianza_clase(
                self.modelo_tipo,
                asunto,
                tipo_nombre,
            )
        )

        # ============================
        # 2. ÁREA DE DESTINO
        # ============================

        area_nombre = str(
            self.modelo_area.predict(
                [asunto]
            )[0]
        )

        if area_nombre not in AREAS:
            raise ValueError(
                f"Área desconocida devuelta "
                f"por el modelo: "
                f"{area_nombre}"
            )

        area_codigo = AREAS[
            area_nombre
        ]

        area_id = demo_id(
            area_codigo
        )

        confianza_area = (
            self._confianza_clase(
                self.modelo_area,
                asunto,
                area_nombre,
            )
        )

        # ============================
        # 3. NORMATIVAS
        # ============================

        texto_vectorizado = (
            self.features_norm.transform(
                [asunto]
            )
        )

        probabilidades_normas = (
            self.modelo_normas.predict_proba(
                texto_vectorizado
            )[0]
        )

        etiquetas = list(
            self.mlb.classes_
        )

        seleccionadas = []

        for etiqueta, probabilidad in zip(
            etiquetas,
            probabilidades_normas,
        ):

            probabilidad = float(
                probabilidad
            )

            if (
                probabilidad
                >= self.umbral_normas
            ):
                seleccionadas.append(
                    (
                        str(etiqueta),
                        probabilidad,
                    )
                )

        # Mayor confianza primero
        seleccionadas.sort(
            key=lambda elemento: elemento[1],
            reverse=True,
        )

        normativas = []

        for orden, (
            etiqueta,
            confianza,
        ) in enumerate(
            seleccionadas,
            start=1,
        ):

            normativa_id = demo_id(
                f"NORMATIVA:{etiqueta}"
            )

            normativas.append(
                NormativaPredicha(
                    normativa_id=normativa_id,
                    confianza=confianza,
                    orden=orden,
                )
            )

        # ============================
        # 4. RESPUESTA DEL PREDICTOR
        # ============================

        return PrediccionContexto(
            solicitud_id=solicitud_id,

            tipo_informe_predicho_id=tipo_id,

            area_destino_predicha_id=area_id,

            confianza_tipo=confianza_tipo,

            confianza_area=confianza_area,

            modelo="SKLEARN_RF_IA_01",

            version_modelo=(
                self.version_modelo
            ),

            parametros={
                "umbral_normas":
                    self.umbral_normas,

                "tipo_predicho":
                    tipo_nombre,

                "area_predicha":
                    area_nombre,

                "asunto":
                    asunto,
            },

            normativas=normativas,
        )