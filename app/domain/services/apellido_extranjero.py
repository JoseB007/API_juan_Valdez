from typing import Dict

from app.utils.constantes import FRASES_GENERICAS, REGION_GENERICA


def apellido_extranjero(apellido_original: str, apellido_normalizado: str) -> Dict:
    return {
    "estado": "no_encontrado",
    "fuente": "Genérico",
    "apellido_original": apellido_original,
    "apellido_normalizado": apellido_normalizado,
    "distribuciones": REGION_GENERICA,
    "frases": FRASES_GENERICAS
}