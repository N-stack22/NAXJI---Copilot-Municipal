from copy import deepcopy
from uuid import UUID

from src.adapters.out.persistence.memoria import Memoria
from src.application.ports.output.informe_repository import InformeRepository
from src.domain.entities.informe import Informe
from src.domain.services.errores import ConflictoEstado


class InformeRepositoryMemory(InformeRepository):
    def __init__(self, memoria: Memoria):
        self.memoria = memoria

    def guardar(self, informe: Informe) -> Informe:
        with self.memoria.lock:
            existente = self.obtener_por_solicitud(informe.solicitud_id)
            if existente and existente.id != informe.id:
                raise ConflictoEstado("Ya existe un informe para esta solicitud")
            numeros = [v.numero_version for v in informe.versiones]
            if len(set(numeros)) != len(numeros) or any(n < 1 for n in numeros):
                raise ConflictoEstado("Número de versión inválido o duplicado")
            self.memoria.informes[informe.id] = deepcopy(informe)
            return deepcopy(informe)

    def obtener_por_id(self, informe_id: UUID) -> Informe | None:
        with self.memoria.lock:
            return deepcopy(self.memoria.informes.get(informe_id))

    def obtener_por_solicitud(self, solicitud_id: UUID) -> Informe | None:
        with self.memoria.lock:
            return deepcopy(next((i for i in self.memoria.informes.values()
                                  if i.solicitud_id == solicitud_id), None))
