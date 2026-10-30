import json

from src.adapters.out.persistence.postgres import entity, save
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

    FILTRO = """(%s OR d.usuario_id=%s OR d.ambito='INSTITUCIONAL'
                   OR (d.ambito='AREA' AND d.area_id=%s))"""

    def crear(self, documento):
        with self.uow.connection(write=True) as c:
            # Serializa la deduplicación incluso entre procesos. No bloquea servicios externos.
            llave = f"{documento.usuario_id}:{documento.ambito}:{documento.area_id}:{documento.sha256}"
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (llave,))
            row = c.execute("""SELECT * FROM public.documentos WHERE usuario_id=%s AND ambito=%s
                            AND area_id IS NOT DISTINCT FROM %s AND sha256=%s""",
                            (documento.usuario_id, documento.ambito, documento.area_id, documento.sha256)).fetchone()
            if row:
                return entity(Documento, row), False
            save(c, "documentos", documento, insert_only=True)
            return documento, True

    def obtener(self, documento_id):
        with self.uow.connection() as c:
            row = c.execute("SELECT * FROM public.documentos WHERE id=%s", (documento_id,)).fetchone()
            return entity(Documento, row) if row else None

    def listar(self, usuario, limite=100, offset=0):
        with self.uow.connection() as c:
            rows = c.execute("SELECT d.* FROM public.documentos d WHERE " + self.FILTRO
                             + " ORDER BY d.created_at DESC,d.id LIMIT %s OFFSET %s",
                             (*self.acceso(usuario), limite, offset)).fetchall()
            return [entity(Documento, r) for r in rows]

    def reservar(self, documento_id, estado, intento, hasta):
        with self.uow.connection(write=True) as c:
            row = c.execute("SELECT estado,reserva_hasta FROM public.documentos WHERE id=%s FOR UPDATE",
                            (documento_id,)).fetchone()
            if not row or (row["reserva_hasta"] and row["reserva_hasta"] > ahora()):
                raise ConflictoEstado("Documento en procesamiento; reintente cuando venza su reserva")
            c.execute("""UPDATE public.documentos SET estado=%s,intento=%s,reserva_hasta=%s,error=NULL,
                         updated_at=now() WHERE id=%s""", (estado, intento, hasta, documento_id))

    def finalizar(self, documento_id, intento, estado, error=None, fragmentos=None, procesamiento=None):
        with self.uow.connection(write=True) as c:
            c.execute("SET LOCAL search_path=public,extensions,pg_catalog")
            row = c.execute("SELECT intento,reserva_hasta FROM public.documentos WHERE id=%s FOR UPDATE",
                            (documento_id,)).fetchone()
            if not row or row["intento"] != intento or row["reserva_hasta"] <= ahora():
                raise ConflictoEstado("El intento documental perdió vigencia; consulte el estado y reintente")
            if fragmentos is not None:
                c.execute("DELETE FROM public.documento_fragmentos WHERE documento_id=%s", (documento_id,))
                for f in fragmentos:
                    c.execute("""INSERT INTO public.documento_fragmentos
                        (id,documento_id,orden,texto,localizacion,inicio,fin,embedding,procesamiento)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s::vector,%s)""",
                        (f["id"], documento_id, f["orden"], f["texto"], f["localizacion"], f["inicio"], f["fin"],
                         json.dumps(f["vector"]), procesamiento))
            c.execute("""UPDATE public.documentos SET estado=%s,error=%s,reserva_hasta=NULL,intento=NULL,
                fragmentos=CASE WHEN %s THEN %s ELSE fragmentos END,
                procesamiento=COALESCE(%s,procesamiento),updated_at=now() WHERE id=%s""",
                (estado, error, fragmentos is not None, len(fragmentos or []), procesamiento, documento_id))

    def contar(self, usuario, procesamiento):
        with self.uow.connection() as c:
            return c.execute("SELECT count(*) AS n FROM public.documentos d WHERE " + self.FILTRO
                             + " AND d.estado='INDEXADO' AND d.procesamiento=%s",
                             (*self.acceso(usuario), procesamiento)).fetchone()["n"]

    def buscar(self, usuario, vector, procesamiento, top_k, umbral):
        with self.uow.connection() as c:
            c.execute("SET LOCAL search_path=public,extensions,pg_catalog")
            # Exact cosine scan: authorization materialized BEFORE ranking/limit. Avoids
            # approximate-index post-filter losses at this corpus size. pgvector is real.
            rows = c.execute("""WITH autorizados AS MATERIALIZED (
                SELECT f.*,d.titulo,d.procedencia,d.sha256,d.tipo,d.nombre_original FROM public.documento_fragmentos f
                JOIN public.documentos d ON d.id=f.documento_id WHERE """ + self.FILTRO + """
                AND d.estado='INDEXADO' AND d.procesamiento=%s AND f.procesamiento=d.procesamiento)
                SELECT *,1-(embedding <=> %s::vector) AS similitud FROM autorizados
                WHERE 1-(embedding <=> %s::vector) >= %s
                ORDER BY embedding <=> %s::vector,id LIMIT %s""",
                (*self.acceso(usuario), procesamiento, json.dumps(vector), json.dumps(vector),
                 umbral, json.dumps(vector), top_k)).fetchall()
            return [{"documento_id": str(r["documento_id"]), "fragmento_id": str(r["id"]),
                     "titulo": r["titulo"], "procedencia": r["procedencia"], "sha256": r["sha256"],
                     "tipo": r["tipo"], "nombre_original": r["nombre_original"],
                     "texto": r["texto"], "localizacion": r["localizacion"], "inicio": r["inicio"],
                     "fin": r["fin"], "similitud": float(r["similitud"])} for r in rows]

    def fragmento(self, documento_id, fragmento_id):
        with self.uow.connection() as c:
            return c.execute("""SELECT id,documento_id,texto,localizacion,inicio,fin,procesamiento
                FROM public.documento_fragmentos WHERE id=%s AND documento_id=%s""",
                (fragmento_id, documento_id)).fetchone()
