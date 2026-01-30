from typing import Dict

from app.integrations.openai_client import OpenAICliente
from app.integrations.gemini_cliente import GeminiIACliente

def obtener_apellido_ai(apellido: str) -> Dict:
    apellido = GeminiIACliente().obtener_apellido(apellido)

    if apellido:
        return apellido
    return None
