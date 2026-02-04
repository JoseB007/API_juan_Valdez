from typing import Dict

from app.domain.models.models import DistribucionApellidoDepartamento, Apellido, Frases
from app.domain.services.obtener_apellido_IA import ObtenerApellidoIA
from app.domain.services.obtener_apellido_API_OPOGRAPG import ObtenerApellidoAPIOpograph


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
    else:
        servicio = ObtenerApellidoAPIOpograph(apellido_normalizado, apellido_original)
        apellido = servicio.ejecutar()

        if apellido['estado'] == "error":
            servicio = ObtenerApellidoIA(apellido_normalizado, apellido_original)
            return servicio.ejecutar()

        return apellido