from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
import re
from uuid import UUID, uuid4, uuid5

from src.application.ports.output.documentos import AlmacenDocumentos, DocumentoRepository, Embeddings, ExtractorDocumentos
from src.application.use_cases.servicios_solicitud import autorizar
from src.domain.entities.documento import Documento, puede_leer
from src.domain.entities.solicitud import ahora
from src.domain.services.errores import ConflictoEstado, DatosInvalidos, ErrorServicio, NoAutorizado, NoEncontrado
from src.domain.value_objects.estados import Rol


def segmentar(unidades, tamano, solapamiento):
    """Ventanas reproducibles por unidad, offsets sobre texto extraído normalizado."""
    resultado = []
    for unidad in unidades:
        texto = unidad["texto"].replace("\r\n", "\n").replace("\r", "\n").strip()
        for inicio in range(0, len(texto), tamano - solapamiento):
            fin = min(inicio + tamano, len(texto))
            if texto[inicio:fin].strip():
                resultado.append({"texto": texto[inicio:fin], "localizacion": unidad["localizacion"],
                                  "inicio": inicio, "fin": fin})
            if fin == len(texto):
                break
    return resultado


class GestionDocumentos:
    def __init__(self, repo: DocumentoRepository, almacen: AlmacenDocumentos, extractor: ExtractorDocumentos,
                 embeddings: Embeddings, config):
        self.repo, self.almacen, self.extractor, self.embeddings, self.config = repo, almacen, extractor, embeddings, config
        self.procesamiento = (f"extract-v1:chars-v1:{config.chunk_size}:{config.chunk_overlap}:"
                              f"{embeddings.modelo}:{embeddings.dimension}:{config.processing_revision}")

    def obtener(self, documento_id, usuario, escritura=False):
        autorizar(usuario, escritura=escritura)
        doc = self.repo.obtener(documento_id)
        if doc is None or not puede_leer(doc, usuario):
            raise NoEncontrado("Documento no encontrado o sin acceso")
        if escritura and doc.usuario_id != usuario.id and Rol.ADMINISTRADOR not in usuario.roles:
            raise NoAutorizado("Solo el propietario o administrador puede procesar el documento")
        return doc

    def listar(self, usuario, limite=100, offset=0):
        autorizar(usuario)
        return self.repo.listar(usuario, limite, offset)

    def cargar(self, usuario, nombre, contenido, titulo, procedencia, ambito):
        autorizar(usuario, escritura=True)
        titulo, procedencia = titulo.strip(), procedencia.strip()
        if not titulo or len(titulo) > 250 or not procedencia or len(procedencia) > 1000:
            raise DatosInvalidos("Indique título (hasta 250 caracteres) y procedencia (hasta 1000)")
        if ambito not in {"PRIVADO", "AREA", "INSTITUCIONAL"}:
            raise DatosInvalidos("Ámbito no válido")
        if ambito == "INSTITUCIONAL" and Rol.ADMINISTRADOR not in usuario.roles:
            raise NoAutorizado("Solo un administrador puede incorporar fuentes institucionales")
        if ambito == "AREA" and usuario.area_id is None:
            raise DatosInvalidos("El perfil no tiene área asignada")
        nombre = (nombre or "").replace("\\", "/").split("/")[-1]
        if not nombre or len(nombre) > 250 or any(ord(c) < 32 for c in nombre):
            raise DatosInvalidos("Nombre de archivo inválido")
        tipo = nombre.rsplit(".", 1)[-1].lower()
        if tipo not in self.config.formats:
            raise DatosInvalidos("Formato no permitido; utilice PDF, DOCX o TXT autorizado")
        if not contenido or len(contenido) > self.config.max_bytes:
            raise DatosInvalidos("Archivo vacío o superior al límite configurado")
        # Validar contenido real ANTES de persistir. No se confía en el MIME del cliente.
        self.extractor.extraer(contenido, tipo)
        nuevo = Documento(titulo, nombre, tipo, len(contenido), sha256(contenido).hexdigest(), usuario.id,
                          procedencia, ambito, usuario.area_id if ambito == "AREA" else None)
        nuevo.ubicacion = f"{usuario.id}/{nuevo.id}/{nuevo.sha256}.{tipo}"
        doc, creada = self.repo.crear(nuevo)
        if not creada and doc.estado not in {"ERROR_CARGA", "SUBIENDO"}:
            return doc
        intento = uuid4()
        self.repo.reservar(doc.id, "SUBIENDO", intento, ahora() + timedelta(seconds=120))
        try:
            self.almacen.guardar(doc.ubicacion, contenido, tipo)
        except ErrorServicio:
            self.repo.finalizar(doc.id, intento, "ERROR_CARGA", "ALMACEN_NO_DISPONIBLE: vuelva a cargar el mismo archivo")
            raise
        self.repo.finalizar(doc.id, intento, "CARGADO")
        return self.obtener(doc.id, usuario)

    def procesar(self, documento_id, usuario):
        doc = self.obtener(documento_id, usuario, escritura=True)
        if doc.estado == "INDEXADO" and doc.procesamiento == self.procesamiento:
            return doc
        if doc.estado in {"SUBIENDO", "ERROR_CARGA"}:
            raise ConflictoEstado("Vuelva a cargar el archivo para completar su almacenamiento")
        intento = uuid4()
        self.repo.reservar(doc.id, "PROCESANDO", intento, ahora() + timedelta(seconds=self.config.lease_seconds))
        try:
            contenido = self.almacen.leer(doc.ubicacion)
            if sha256(contenido).hexdigest() != doc.sha256:
                raise DatosInvalidos("El archivo almacenado no coincide con su hash")
            fragmentos = segmentar(self.extractor.extraer(contenido, doc.tipo),
                                   self.config.chunk_size, self.config.chunk_overlap)
            if not fragmentos or len(fragmentos) > self.config.max_chunks:
                raise DatosInvalidos("Cantidad de fragmentos no permitida")
            # Llamadas externas fuera de transacciones. Publicación atómica por intento.
            vectores = []
            for inicio in range(0, len(fragmentos), 16):
                vectores.extend(self.embeddings.codificar([f["texto"] for f in fragmentos[inicio:inicio+16]]))
            if len(vectores) != len(fragmentos):
                raise ErrorServicio("EMBEDDINGS_INVALIDOS", "Embeddings incompletos; reintente el procesamiento")
            for orden, (fragmento, vector) in enumerate(zip(fragmentos, vectores)):
                fragmento.update(id=uuid5(doc.id, f"{self.procesamiento}:{orden}:{sha256(fragmento['texto'].encode()).hexdigest()}"),
                                 orden=orden, vector=vector)
            self.repo.finalizar(doc.id, intento, "INDEXADO", fragmentos=fragmentos, procesamiento=self.procesamiento)
        except (ErrorServicio, DatosInvalidos) as error:
            self.repo.finalizar(doc.id, intento, "ERROR_PROCESAMIENTO", str(error))
            raise
        except ConflictoEstado:
            raise
        except Exception:
            self.repo.finalizar(doc.id, intento, "ERROR_PROCESAMIENTO", "PROCESAMIENTO_FALLIDO: reintente")
            raise ErrorServicio("PROCESAMIENTO_FALLIDO", "No se pudo procesar el documento; reintente") from None
        return self.obtener(doc.id, usuario)

    def original(self, documento_id, usuario):
        doc = self.obtener(documento_id, usuario)
        contenido = self.almacen.leer(doc.ubicacion)
        if sha256(contenido).hexdigest() != doc.sha256:
            raise ErrorServicio("ALMACEN_INTEGRIDAD", "El original no coincide con el hash registrado")
        return doc, contenido

    def fragmento(self, documento_id, fragmento_id, usuario):
        self.obtener(documento_id, usuario)
        fragmento = self.repo.fragmento(documento_id, fragmento_id)
        if fragmento is None:
            raise NoEncontrado("Fragmento no encontrado; consulte el snapshot de la versión")
        return fragmento

    def recuperar(self, consulta, usuario):
        autorizar(usuario)
        if not consulta.strip() or len(consulta) > 12000:
            raise DatosInvalidos("La consulta debe tener entre 1 y 12000 caracteres")
        cantidad = self.repo.contar(usuario, self.procesamiento)
        if not cantidad:
            return {"estado": "CORPUS_VACIO", "fuentes": [], "procesamiento": self.procesamiento}
        vector = self.embeddings.codificar([consulta])[0]
        candidatos = self.repo.buscar(usuario, vector, self.procesamiento, self.config.top_k, self.config.threshold)
        fuentes, total = [], 0
        for candidato in candidatos:
            # No truncar una cita a escondidas. Todo snapshot corresponde al texto enviado.
            if total + len(candidato["texto"]) > self.config.context_chars:
                continue
            total += len(candidato["texto"])
            fuentes.append({**candidato, "citas": []})
        return {"estado": "RECUPERADO" if fuentes else "SIN_RESULTADOS", "fuentes": fuentes,
                "procesamiento": self.procesamiento, "umbral_similitud": self.config.threshold}

    def proteger(self, informe, usuario):
        informe = deepcopy(informe)
        for version in informe.versiones:
            if version.sustento:
                for fuente in version.sustento["fuentes"]:
                    doc = self.repo.obtener(UUID(fuente["documento_id"]))
                    if doc is None or not puede_leer(doc, usuario):
                        fuente.clear()
                        fuente.update(sin_acceso=True, citas=[])
        return informe


MARCADOR_CITA = re.compile(r"\[F:([^\]\n]+)\]")


def vincular_citas(contenido, recuperacion, citas=()):
    """Cada marcador incluye el UUID estable del fragmento autorizado."""
    resultado = deepcopy(recuperacion)
    permitidas = {f["fragmento_id"]: f for f in resultado["fuentes"]}
    for cita in citas:
        if (not isinstance(cita, dict) or not isinstance(cita.get("fragmento_id"), str)
                or cita["fragmento_id"] not in permitidas):
            raise ErrorServicio("CITA_DESCONOCIDA", "El modelo citó una fuente ajena al contexto; no se guardó el borrador")
        seccion = cita.get("seccion")
        if (not isinstance(seccion, str) or seccion not in contenido
                or not isinstance(contenido[seccion], str) or not contenido[seccion].strip()):
            raise ErrorServicio("CITA_INVALIDA", "Una cita no corresponde al pasaje o al texto fuente; no se guardó el borrador")
        marcador = f"[F:{cita['fragmento_id']}]"
        if marcador not in contenido[seccion]:
            contenido[seccion] += " " + marcador
    for seccion, texto in contenido.items():
        if not isinstance(texto, str):
            continue
        for match in MARCADOR_CITA.finditer(texto):
            if match[1] not in permitidas:
                raise ErrorServicio("CITA_DESCONOCIDA", "El modelo citó una fuente ajena al contexto; no se guardó el borrador")
            if not any(c["seccion"] == seccion for c in permitidas[match[1]]["citas"]):
                permitidas[match[1]]["citas"].append({"seccion": seccion, "pasaje": texto,
                                                    "estado": "PENDIENTE_REVISION"})
    resultado["advertencia"] = "Las citas identifican referencias; requieren revisión humana y no verifican hechos ni vigencia normativa."
    return resultado


def sustento_editado(anterior, contenido):
    resultado = deepcopy(anterior.sustento)
    if resultado:
        for fuente in resultado["fuentes"]:
            for cita in fuente["citas"]:
                if anterior.contenido.get(cita["seccion"]) != contenido.get(cita["seccion"]):
                    cita["estado"] = "TEXTO_MODIFICADO"
        resultado["advertencia"] = "Edición humana: las secciones modificadas requieren revisar sus citas. No se verificó su sustento automáticamente."
    return resultado
