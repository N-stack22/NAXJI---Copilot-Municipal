"""Dobles explícitos para tests; nunca se componen en producción."""
from copy import deepcopy
from math import sqrt
from threading import RLock

from src.domain.entities.documento import puede_leer
from src.domain.entities.solicitud import ahora
from src.domain.services.errores import ConflictoEstado, ErrorServicio


class AlmacenMemoria:
    def __init__(self):
        self.archivos = {}
        self.fallar = False

    def guardar(self, ubicacion, contenido, tipo):
        if self.fallar:
            raise ErrorServicio("ALMACEN_NO_DISPONIBLE", "Almacén de prueba caído")
        self.archivos[ubicacion] = contenido

    def leer(self, ubicacion):
        if self.fallar:
            raise ErrorServicio("ALMACEN_NO_DISPONIBLE", "Almacén de prueba caído")
        return self.archivos[ubicacion]


class EmbeddingsPrueba:
    modelo = "DOBLE-PRUEBA-NO-SEMANTICO"
    dimension = 1024

    def __init__(self):
        self.fallar = False
        self.llamadas = 0

    def codificar(self, textos):
        self.llamadas += 1
        if self.fallar:
            raise ErrorServicio("EMBEDDINGS_NO_DISPONIBLES", "Embeddings de prueba caídos")
        vectores = []
        for texto in textos:
            x = [float(any(p in texto.lower() for p in palabras)) for palabras in
                 [("parque", "ambiental", "residuos"), ("tribut", "impuesto"), ("licencia", "obra")]]
            if not any(x):
                x = [0, 0, 1]
            norma = sqrt(sum(v*v for v in x))
            vectores.append([v/norma for v in x] + [0.0]*1021)
        return vectores


class DocumentosMemoria:
    def __init__(self):
        self.documentos, self.fragmentos = {}, {}
        self.lock = RLock()

    def crear(self, doc):
        with self.lock:
            previo = next((d for d in self.documentos.values() if
                           (d.usuario_id, d.ambito, d.area_id, d.sha256) ==
                           (doc.usuario_id, doc.ambito, doc.area_id, doc.sha256)), None)
            if previo:
                return deepcopy(previo), False
            self.documentos[doc.id] = deepcopy(doc)
            return deepcopy(doc), True

    def obtener(self, doc_id):
        return deepcopy(self.documentos.get(doc_id))

    def listar(self, usuario, limite=100, offset=0):
        return deepcopy([d for d in self.documentos.values() if puede_leer(d, usuario)][offset:offset+limite])

    def reservar(self, doc_id, estado, intento, hasta):
        with self.lock:
            doc = self.documentos[doc_id]
            if doc.reserva_hasta and doc.reserva_hasta > ahora():
                raise ConflictoEstado("Documento en procesamiento")
            doc.estado, doc.intento, doc.reserva_hasta, doc.error = estado, intento, hasta, None

    def finalizar(self, doc_id, intento, estado, error=None, fragmentos=None, procesamiento=None):
        with self.lock:
            doc = self.documentos[doc_id]
            if doc.intento != intento or doc.reserva_hasta <= ahora():
                raise ConflictoEstado("Intento vencido")
            if fragmentos is not None:
                self.fragmentos[doc_id] = deepcopy(fragmentos)
                doc.fragmentos = len(fragmentos)
            doc.estado, doc.error, doc.reserva_hasta, doc.intento = estado, error, None, None
            if procesamiento:
                doc.procesamiento = procesamiento

    def contar(self, usuario, procesamiento):
        return sum(d.estado == "INDEXADO" and d.procesamiento == procesamiento for d in self.listar(usuario))

    def buscar(self, usuario, vector, procesamiento, top_k, umbral):
        resultados = []
        for doc in self.listar(usuario):
            if doc.estado != "INDEXADO" or doc.procesamiento != procesamiento:
                continue
            for fragmento in self.fragmentos[doc.id]:
                similitud = sum(x*y for x, y in zip(vector, fragmento["vector"]))
                if similitud >= umbral:
                    resultados.append({"documento_id": str(doc.id), "fragmento_id": str(fragmento["id"]),
                        "titulo": doc.titulo, "procedencia": doc.procedencia, "sha256": doc.sha256,
                        "texto": fragmento["texto"], "localizacion": fragmento["localizacion"],
                        "inicio": fragmento["inicio"], "fin": fragmento["fin"], "similitud": similitud})
        return sorted(resultados, key=lambda r: (-r["similitud"], r["fragmento_id"]))[:top_k]

    def fragmento(self, doc_id, fragmento_id):
        f = next((deepcopy(f) for f in self.fragmentos.get(doc_id, []) if f["id"] == fragmento_id), None)
        if f is not None:
            return {k: f[k] for k in ("id", "texto", "localizacion", "inicio", "fin")} | {
                "documento_id": doc_id, "procesamiento": self.documentos[doc_id].procesamiento}
        return None
