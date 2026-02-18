from typing import Dict

# from app.integrations.openai_client import OpenAICliente
from app.integrations.gemini_cliente import GeminiIACliente
from app.schemas.ai_apellido_distro_schema import AI_APELLIDO_DISTRO_SCHEMA
from app.schemas.ai_frases_schema import AI_FRASES_SCHEMA
from app.schemas.ai_batch_frases_schema import AI_BATCH_FRASES_SCHEMA


def generar_apellido_ia(apellido: str) -> Dict:
    return GeminiIACliente(schema=AI_APELLIDO_DISTRO_SCHEMA).obtener_apellido_distribuciones(apellido)


def generar_frases_ia(apellido: str, dist: Dict) -> Dict:
    return GeminiIACliente(schema=AI_FRASES_SCHEMA).obtener_frases_apellido(apellido, dist)


def generar_frases_batch_ia(apellidos_con_dist: list) -> Dict:
    return GeminiIACliente(schema=AI_BATCH_FRASES_SCHEMA).obtener_frases_batch(apellidos_con_dist)