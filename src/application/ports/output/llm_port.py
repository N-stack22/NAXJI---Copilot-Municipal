from abc import ABC, abstractmethod


class LLMPort(ABC):

    @abstractmethod
    def generar(self, prompt: str) -> str:
        """
        Genera una respuesta utilizando un modelo de lenguaje.
        """
        pass