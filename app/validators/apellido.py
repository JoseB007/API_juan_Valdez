import re
import unicodedata
from typing import Optional, Dict


APELLIDO_REGEX = re.compile(r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,30}$')


def remover_acentos(apellido: str) -> str:
    """
    Elimina tildes y diacríticos.
    Ej: 'GÓMEZ' -> 'GOMEZ'
    """
    normalizado = unicodedata.normalize("NFD", apellido)
    return "".join(
        char for char in normalizado
        if unicodedata.category(char) != "Mn"
    )


def validar_apellido(apellido: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Valida y normaliza un apellido según las reglas del MVP.
    """

    # Campo obligatorio
    if not apellido:
        return {
            "es_valido": False,
            "error": "El apellido es obligatorio",
            "normalizado": None
        }

    # Espacios al inicio o fin
    if apellido != apellido.strip():
        return {
            "es_valido": False,
            "error": "El apellido no debe contener espacios al inicio o al final",
            "normalizado": None
        }

    # Regex principal
    if not APELLIDO_REGEX.match(apellido):
        return {
            "es_valido": False,
            "error": (
                "El apellido debe tener entre 2 y 30 letras y no contener espacios ni caracteres especiales"
            ),
            "normalizado": None
        }

    # Normalización
    apellido_upper = apellido.upper()
    apellido_normalizado = remover_acentos(apellido_upper)

    return {
        "es_valido": True,
        "error": None,
        "normalizado": apellido_normalizado
    }
