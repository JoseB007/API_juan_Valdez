from typing import Dict

from app.integrations.openai_client import OpenAICliente
from app.integrations.gemini_cliente import GeminiIACliente
from app.schemas.ai_response_schema import AI_RESPONSE_SCHEMA
from app.schemas.ai_frases_schema import AI_FRASES_SCHEMA


def obtener_apellido_ai(apellido: str) -> Dict:
    apellido = GeminiIACliente(schema=AI_RESPONSE_SCHEMA).obtener_apellido_distribuciones(apellido)

    if apellido:
        return apellido
    return None

def obtener_frases_ai(apellido: str, dist: Dict) -> Dict:
    frases = GeminiIACliente(schema=AI_FRASES_SCHEMA).obtener_frases_apellido(apellido, dist)

    if frases:
        return frases
    return None