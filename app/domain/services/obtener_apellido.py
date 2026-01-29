from typing import Optional, Dict

from app.domain.models.models import DistribucionApellidoDepartamento, Apellido, Frases

def obtener_informacion_apellido(apellido_normalizado: str, apellido_original: str) -> Dict:
    apellido_obj = Apellido.objects.filter(apellido=apellido_normalizado).first()

    if apellido_obj:
        distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
        frases = Frases.objects.filter(apellido=apellido_obj)

        return {
            "estado": "encontrado",
            "origen": apellido_obj.origen,
            "apellido_original": apellido_original,
            "apellido_normalizado": apellido_obj.apellido,
            "departamentos": distribuciones,
            "frases": frases
        }
    
    return {
        "estado": "no_encontrado",
        "origen": "IA",
        "apellido_original": apellido_original,
        "apellido_normalizado": apellido_normalizado,
        "departamentos": [
            {"departamento": "Caldas", "porcentaje": 40.0, "ranking": 1, "origen": "IA"},
            {"departamento": "Cundinamarca", "porcentaje": 36.0, "ranking": 2, "origen": "IA"},
            {"departamento": "Magdalena", "porcentaje": 24.0, "ranking": 3, "origen": "IA"},
        ],
        "frases": [
            {"categoria": "PERSONALIDAD", "frase": "Cada historia comienza con un nombre.", "origen": "IA"},
            {"categoria": "SABOR", "frase": "Descubre tu sabor único.", "origen": "IA"}
        ]
    }