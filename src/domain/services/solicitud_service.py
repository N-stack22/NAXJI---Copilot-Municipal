from src.domain.entities.solicitud import Solicitud


class SolicitudService:

    @staticmethod
    def validar(solicitud: Solicitud) -> None:
        if not solicitud.asunto.strip():
            raise ValueError("El asunto es obligatorio")

        if not solicitud.descripcion.strip():
            raise ValueError("La descripción es obligatoria")