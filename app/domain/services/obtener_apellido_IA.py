from typing import Dict
from jsonschema import validate, ValidationError

from app.domain.models.models import (
    Apellido,
    Departamento,
    DistribucionApellidoDepartamento,
    Frases
)

from app.integrations.ai_cliente import obtener_apellido_ai
from app.schemas.ai_response_schema import AI_RESPONSE_SCHEMA


class ObtenerApellidoIA:
    def __init__(self, apellido_normalizado: str, apellido_original: str):
        self.apellido_normalizado = apellido_normalizado
        self.apellido_original = apellido_original

    def ejecutar(self) -> Dict:
        ai_response = obtener_apellido_ai(self.apellido_normalizado)
        
        if ai_response:
            # self._validar_ai_response(ai_response)

            # return self._crear_apellido(ai_response)

            return {
                "estado": "no_encontrado",
                "origen": ai_response['origen'],
                "apellido_original": self.apellido_original,
                "apellido_normalizado": self.apellido_normalizado,
                "departamentos": [
                    {
                        "departamento": dist['departamento'], 
                        "porcentaje": dist['porcentaje'],
                        "ranking": dist['ranking'], 
                        "origen": "IA"
                    } for dist in ai_response['distribuciones']
                ],
                "frases": [
                    {
                        "categoria": f['categoria'], 
                        "frase": f['texto'], 
                        "origen": "IA"
                    } for f in ai_response['frases']
                ]
            }

        else:
            return {
                "estado": "no_encontrado",
                "origen": "IA",
                "apellido_original": self.apellido_original,
                "apellido_normalizado": self.apellido_normalizado,
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
        
    def _validar_ai_response(self, ai_response: Dict):
        try:
            validate(instance=ai_response, schema=AI_RESPONSE_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"Error al validar la respuesta del AI: {e}")

    def _crear_apellido(self, ai_response: Dict) -> Apellido:
        apellido_obj, _ = Apellido.objects.get_or_create(
            apellido=ai_response['apellido'],
            origen=ai_response['origen'],
        )

        for dist in ai_response['distribuciones']:
            departamento, _ = Departamento.objects.get_or_create(
                nombre=dist['departamento']
            )
            DistribucionApellidoDepartamento.objects.get_or_create(
                apellido=apellido_obj,
                departamento=departamento,
                porcentaje=dist['porcentaje'],
                ranking=dist['ranking'],
                origen='IA',
            )

        for frase in ai_response['frases']:
            Frases.objects.create(
                categoria=frase['categoria'],
                frase=frase('texto'),
                origen='IA',
                apellido=apellido_obj,
            )

        return apellido_obj
        