from typing import Optional, Dict


def obtener_informacion_apellido(apellido_normalizado: str, apellido_original: str) -> Dict[str, Optional[str]]:
    """
    Obtiene la información de un apellido según el apellido normalizado.
    """

    # Simulación de apellidos existentes
    if apellido_normalizado == "GOMEZ":
        return {
            "estado": "encontrado",
            "apellido_original": apellido_original,
            "apellido_normalizado": apellido_normalizado,
            "departamentos": [
                {"nombre": "Caldas", "porcentaje": 40, "rango": 15},
                {"nombre": "Cundinamarca", "porcentaje": 36, "rango": 22},
                {"nombre": "Magdalena", "porcentaje": 24, "rango": 30},
            ],
            "frases": {
                "personalidad": "Soy fuerte, soy cálido, soy honesto.",
                "sabor": "El chocolate negro habla de profundidad, carácter y fuerza interior."
            }
        }

    return {
        "estado": "no_encontrado",
        "apellido_original": apellido_original,
        "apellido_normalizado": apellido_normalizado,
        "departamentos": [],
        "mensaje": "Tu apellido es poco común, lo que lo hace especial.",
        "frases": {
            "personalidad": "Cada historia comienza con un nombre.",
            "sabor": "Descubre tu sabor único."
        }
    }