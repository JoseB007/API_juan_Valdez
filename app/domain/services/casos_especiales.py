from typing import Dict
from app.utils.constantes import FRASES_GENERICAS, REGION_GENERICA

def apellido_extranjero(apellido_original: str, apellido_normalizado: str) -> Dict:
    """Retorna un resultado genérico para apellidos extranjeros."""
    return {
        "estado": "no_encontrado",
        "fuente": "Genérico",
        "apellido_original": apellido_original,
        "apellido_normalizado": apellido_normalizado,
        "distribuciones": REGION_GENERICA,
        "frases": FRASES_GENERICAS
    }

def apellido_no_encontrado(apellido_original: str, apellido_normalizado: str) -> Dict:
    """Retorna un resultado genérico cuando no se encuentra el apellido."""
    return {
        "estado": "no_encontrado",
        "fuente": "",
        "apellido_original": apellido_original,
        "apellido_normalizado": apellido_normalizado,
        "distribuciones": REGION_GENERICA,
        "frases": FRASES_GENERICAS
    }
