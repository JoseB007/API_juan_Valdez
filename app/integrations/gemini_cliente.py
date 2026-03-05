import json

from google import genai

from.adaptadorIA import AdaptadorIA
from .utils import SYSTEM_INSTRUCTION


class GeminiIACliente(AdaptadorIA):
    def __init__(self, api_key, modelo, schema):
        self.config_generacion = {
            "response_mime_type": "application/json",
            "response_schema": schema,
            "temperature": 0.1,
            "system_instruction": SYSTEM_INSTRUCTION
        }
        super().__init__(api_key, modelo, schema)

    def _configurar_cliente(self) -> genai:
        return genai.Client(api_key=self.api_key)

    def _ejecutar_modelo(self, prompt: str):
        response = self.cliente.models.generate_content(
            model=self.modelo,
            contents=prompt,
            config=self.config_generacion
        )

        return json.loads(response.text)
