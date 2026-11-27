"""PDF del mismo contenido Word guardado; no genera ni resume texto con IA."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from threading import Lock

import reportlab
from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from src.application.ports.output.exportador_informe import ExportadorInforme
from src.adapters.out.documents.exportador_docx import ExportadorDocx

_lock = Lock()


class ExportadorPdf(ExportadorInforme):
    def exportar(self, informe, version):
        # Misma proyección que Word, incluidos textos de tablas y fuentes autorizadas.
        documento = Document(BytesIO(ExportadorDocx().exportar(informe, version)))
        with _lock:
            if "NaxjiVera" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("NaxjiVera", str(Path(reportlab.__file__).parent / "fonts/Vera.ttf")))
        estilo = ParagraphStyle("NAXJI", fontName="NaxjiVera", fontSize=10, leading=15,
                                textColor=colors.black, spaceAfter=7, splitLongWords=True)
        salida = BytesIO()
        pdf = SimpleDocTemplate(salida, pagesize=A4, rightMargin=54, leftMargin=54,
                                topMargin=45, bottomMargin=45, title=version.titulo or "Informe", author="NAXJI")
        bloques = []
        for p in documento.element.body.iterchildren():
            # El recorrido de párrafos incluye las celdas sin exponer metadatos técnicos.
            for parrafo in ([p] if p.tag.endswith("}p") else p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")):
                texto = "".join(n.text or "" if n.tag.endswith("}t") else "\n" if n.tag.endswith("}br") else "\t"
                                for n in parrafo.iter() if n.tag.rsplit("}", 1)[-1] in {"t", "br", "tab"})
                if texto:
                    bloques.append(Paragraph(escape(texto).replace("\n", "<br/>"), estilo))
                else:
                    bloques.append(Spacer(1, 4))
        def pie(canvas, doc):
            canvas.setFont("NaxjiVera", 8)
            canvas.drawRightString(A4[0]-54, 24, f"NAXJI · Versión {version.numero_version} · Página {doc.page}")
        pdf.build(bloques, onFirstPage=pie, onLaterPages=pie)
        return salida.getvalue()
