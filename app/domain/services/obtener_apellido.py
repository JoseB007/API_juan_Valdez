from typing import Dict

from app.domain.models.models import DistribucionApellidoDepartamento, Apellido, Frases
from app.domain.services.obtener_apellido_IA import ObtenerApellidoIA
from app.domain.services.obtener_apellido_API_OPOGRAPG import ObtenerApellidoAPIOnograph
from app.domain.services.apellido_no_encontrado import apellido_no_encontrado


def obtener_informacion_apellido(apellido_normalizado: str, apellido_original: str) -> Dict:
    apellido_obj, created = Apellido.objects.get_or_create(
        apellido=apellido_normalizado,
        defaults={'estado': Apellido.PENDIENTE, 'fuente': 'Buscando...'}
    )

    if not created:

        if apellido_obj.estado == Apellido.LISTO:
            distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
            frases = Frases.objects.filter(apellido=apellido_obj)

            return {
                "estado": "encontrado",
                "fuente": apellido_obj.fuente,
                "apellido_original": apellido_original,
                "apellido_normalizado": apellido_obj.apellido,
                "distribuciones": list(distribuciones),
                "frases": list(frases)
            }
        
        if apellido_obj.estado == Apellido.PENDIENTE:
            return {
                "estado": "procesando",
                "fuente": "",
                "apellido_original": apellido_original,
                "apellido_normalizado": apellido_normalizado,
                "distribuciones": [],
                "frases": []
            }
        
        apellido_obj.estado = Apellido.PENDIENTE
        apellido_obj.save()

    servicio = ObtenerApellidoAPIOnograph(apellido_normalizado, apellido_original)
    resultado = servicio.ejecutar()

    if resultado.get('estado') == "no_encontrado":
        servicio_ia = ObtenerApellidoIA(apellido_normalizado, apellido_original)
        return servicio_ia.ejecutar()

    return resultado


def consultar_estado_apellido(apellido_normalizado: str, apellido_original: str) -> Dict:
    try:
        apellido_obj = Apellido.objects.get(apellido=apellido_normalizado)
        
        if apellido_obj.estado == Apellido.LISTO:
            distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
            frases = Frases.objects.filter(apellido=apellido_obj)

            return {
                "estado": "encontrado",
                "fuente": apellido_obj.fuente,
                "apellido_original": apellido_original,
                "apellido_normalizado": apellido_obj.apellido,
                "distribuciones": list(distribuciones),
                "frases": list(frases)
            }
        
        if apellido_obj.estado == Apellido.PENDIENTE:
            return {
                "estado": "procesando",
                "fuente": "",
                "apellido_original": apellido_original,
                "apellido_normalizado": apellido_normalizado,
                "distribuciones": [],
                "frases": []
            }
        
        return {
            "estado": "error",
            "fuente": "",
            "apellido_original": apellido_original,
            "apellido_normalizado": apellido_normalizado,
            "distribuciones": [],
            "frases": [],
            "mensaje": "El procesamiento del apellido falló."
        }
        
    except Apellido.DoesNotExist:
        return apellido_no_encontrado()