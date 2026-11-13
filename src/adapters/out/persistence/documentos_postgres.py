import json

from src.adapters.out.persistence.postgres import entity, save
from src.adapters.out.persistence.sql_resources import consulta
from src.domain.entities.documento import Documento
from src.domain.entities.solicitud import ahora
from src.domain.services.errores import ConflictoEstado
from src.domain.value_objects.estados import Rol


class DocumentosPostgres:
    def __init__(self, uow):
        self.uow = uow

    @staticmethod
    def acceso(usuario):
        return (Rol.ADMINISTRADOR in usuario.roles, usuario.id, usuario.area_id)

    def crear(self, documento):
        with self.uow.connection(write=True) as c:
            # Serializa la deduplicación incluso entre procesos. No bloquea servicios externos.
            llave = f"{documento.usuario_id}:{documento.ambito}:{documento.area_id}:{documento.sha256}"
            c.execute(consulta("documentos_postgres", "bloquear_deduplicacion"), (llave,))
            row = c.execute(consulta("documentos_postgres", "buscar_duplicado"),
                            (documento.usuario_id, documento.ambito, documento.area_id, documento.sha256)).fetchone()
            if row:
                return entity(Documento, row), False
            save(c, "documentos", documento, insert_only=True)
            return documento, True

    def obtener(self, documento_id):
        with self.uow.connection() as c:
            row = c.execute(consulta("documentos_postgres", "obtener"), (documento_id,)).fetchone()
            return entity(Documento, row) if row else None

    def listar(self, usuario, limite=100, offset=0):
        with self.uow.connection() as c:
            rows = c.execute(consulta("documentos_postgres", "listar"),
                             (*self.acceso(usuario), limite, offset)).fetchall()
            return [entity(Documento, r) for r in rows]

    def reservar(self, documento_id, estado, intento, hasta):
        with self.uow.connection(write=True) as c:
            row = c.execute(consulta("documentos_postgres", "bloquear_reserva"),
                            (documento_id,)).fetchone()
            if not row or (row["reserva_hasta"] and row["reserva_hasta"] > ahora()):
                raise ConflictoEstado("Documento en procesamiento; reintente cuando venza su reserva")
            c.execute(consulta("documentos_postgres", "reservar"), (estado, intento, hasta, documento_id))

    def finalizar(self, documento_id, intento, estado, error=None, fragmentos=None, procesamiento=None):
        with self.uow.connection(write=True) as c:
            c.execute(consulta("documentos_postgres", "configurar_pgvector"))
            row = c.execute(consulta("documentos_postgres", "bloquear_finalizacion"),
                            (documento_id,)).fetchone()
            if not row or row["intento"] != intento or row["reserva_hasta"] <= ahora():
                raise ConflictoEstado("El intento documental perdió vigencia; consulte el estado y reintente")
            if fragmentos is not None:
                c.execute(consulta("documentos_postgres", "eliminar_fragmentos"), (documento_id,))
                for f in fragmentos:
                    c.execute(consulta("documentos_postgres", "insertar_fragmento"),
                        (f["id"], documento_id, f["orden"], f["texto"], f["localizacion"], f["inicio"], f["fin"],
                         json.dumps(f["vector"]), procesamiento))
            c.execute(consulta("documentos_postgres", "finalizar"),
                (estado, error, fragmentos is not None, len(fragmentos or []), procesamiento, documento_id))

    def contar(self, usuario, procesamiento):
        with self.uow.connection() as c:
            return c.execute(consulta("documentos_postgres", "contar"),
                             (*self.acceso(usuario), procesamiento)).fetchone()["n"]

    def buscar(self, usuario, vector, procesamiento, top_k, umbral):
        with self.uow.connection() as c:
            c.execute(consulta("documentos_postgres", "configurar_pgvector"))
            # Exact cosine scan: authorization materialized BEFORE ranking/limit. Avoids
            # approximate-index post-filter losses at this corpus size. pgvector is real.
            rows = c.execute(consulta("documentos_postgres", "buscar"),
                (*self.acceso(usuario), procesamiento, json.dumps(vector), json.dumps(vector),
                 umbral, json.dumps(vector), top_k)).fetchall()
            return [{"documento_id": str(r["documento_id"]), "fragmento_id": str(r["id"]),
                     "titulo": r["titulo"], "procedencia": r["procedencia"], "sha256": r["sha256"],
                     "tipo": r["tipo"], "nombre_original": r["nombre_original"],
                     "texto": r["texto"], "localizacion": r["localizacion"], "inicio": r["inicio"],
                     "fin": r["fin"], "similitud": float(r["similitud"])} for r in rows]

    def fragmento(self, documento_id, fragmento_id):
        with self.uow.connection() as c:
            return c.execute(consulta("documentos_postgres", "fragmento"),
                (fragmento_id, documento_id)).fetchone()
