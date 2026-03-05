from typing import Dict

from .factory import IAFactory
from .utils import (
    obtener_apellido_distribuciones,
    obtener_frases_batch
)

from app.schemas.ai_apellido_distro_schema import AI_APELLIDO_DISTRO_SCHEMA
from app.schemas.ai_batch_frases_schema import AI_BATCH_FRASES_SCHEMA


def generar_apellido_ia(apellido: str) -> Dict:
    cliente_ia = IAFactory.obtener_cliente(AI_APELLIDO_DISTRO_SCHEMA)
    prompt = obtener_apellido_distribuciones(apellido)
    return cliente_ia.ejecutar(prompt)

def generar_frases_batch_ia(apellidos_con_dist: list) -> Dict:
    cliente_ia = IAFactory.obtener_cliente(AI_BATCH_FRASES_SCHEMA)
    prompt = obtener_frases_batch(apellidos_con_dist)
    return cliente_ia.ejecutar(prompt)
