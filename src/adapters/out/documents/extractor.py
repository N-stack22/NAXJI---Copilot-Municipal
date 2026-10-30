from io import BytesIO
from zipfile import ZipFile, BadZipFile

from src.domain.services.errores import DatosInvalidos


class ExtractorArchivos:
    def extraer(self, contenido, tipo):
        try:
            if tipo == "txt":
                texto = contenido.decode("utf-8-sig")
                if any(ord(c) < 32 and c not in "\n\r\t" for c in texto):
                    raise ValueError("binario")
                unidades = [{"texto": p, "localizacion": f"Párrafo {i}"}
                            for i, p in enumerate(texto.replace("\r\n", "\n").split("\n\n"), 1) if p.strip()]
            elif tipo == "docx":
                # Limitar expansión antes de que python-docx descomprima el contenedor.
                with ZipFile(BytesIO(contenido)) as archivo:
                    if (sum(i.file_size for i in archivo.infolist()) > 50 * 1024 * 1024
                            or len(archivo.infolist()) > 3000):
                        raise ValueError("expansión excesiva")
                    if "word/document.xml" not in archivo.namelist():
                        raise ValueError("no es DOCX")
                from docx import Document
                from docx.table import Table
                from docx.text.paragraph import Paragraph
                doc = Document(BytesIO(contenido))
                unidades = []
                for i, bloque in enumerate(doc.element.body, 1):
                    if bloque.tag.endswith('}p'):
                        texto = Paragraph(bloque, doc).text
                        loc = f"Párrafo/bloque {i}"
                    elif bloque.tag.endswith('}tbl'):
                        tabla = Table(bloque, doc)
                        texto = "\n".join(" | ".join(c.text for c in f.cells) for f in tabla.rows)
                        loc = f"Tabla/bloque {i}"
                    else:
                        continue
                    if texto.strip():
                        unidades.append({"texto": texto, "localizacion": loc})
            elif tipo == "pdf":
                from pypdf import PdfReader
                if not contenido.startswith(b"%PDF-"):
                    raise ValueError("no es PDF")
                pdf = PdfReader(BytesIO(contenido), strict=True)
                if pdf.is_encrypted or len(pdf.pages) > 500:
                    raise ValueError("PDF cifrado o demasiado extenso")
                unidades = []
                for i, pagina in enumerate(pdf.pages, 1):
                    texto = pagina.extract_text() or ""
                    # Rechaza también PDFs mixtos; no publica silenciosamente páginas omitidas.
                    if not texto.strip():
                        raise DatosInvalidos(f"PDF sin texto extraíble en página {i}; requiere OCR no disponible en PMV2")
                    unidades.append({"texto": texto, "localizacion": f"Página {i}"})
            else:
                raise ValueError("formato")
            if not unidades or sum(len(u["texto"]) for u in unidades) > 2_000_000:
                raise ValueError("vacío o demasiado texto")
            return unidades
        except DatosInvalidos:
            raise
        except (Exception, BadZipFile):
            raise DatosInvalidos("Archivo vacío, corrupto, cifrado o incompatible; TXT requiere UTF-8") from None
