import httpx

from src.application.ports.output.llm_port import LLMPort


class OllamaAdapter(LLMPort):

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    def generar(self, prompt: str) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=300.0
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]