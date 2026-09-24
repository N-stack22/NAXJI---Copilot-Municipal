from src.application.ports.output.llm_port import LLMPort


class GenerarBorrador:

    def __init__(self, llm: LLMPort):
        self.llm = llm

    def ejecutar(self, asunto: str, descripcion: str) -> str:

        prompt = f"""
Eres un asistente de inteligencia artificial para una municipalidad.

Genera un borrador formal de respuesta administrativa utilizando la
siguiente información:

Asunto:
{asunto}

Descripción:
{descripcion}

El borrador debe:
- Estar redactado en español.
- Tener un tono formal y administrativo.
- Ser claro y ordenado.
- No inventar datos que no hayan sido proporcionados.
- Servir como borrador para posterior revisión humana.

Genera únicamente el borrador.
"""

        return self.llm.generar(prompt)