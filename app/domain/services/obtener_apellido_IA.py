from typing import Dict
from jsonschema import validate, ValidationError
from django.db import transaction

from app.domain.models.models import (
    Apellido,
    Departamento,
    DistribucionApellidoDepartamento,
    Frases
)

from app.integrations.ai_cliente import generar_apellido_ia
from app.schemas.ai_apellido_distro_schema import AI_APELLIDO_DISTRO_SCHEMA
from app.domain.services.apellido_no_encontrado import apellido_no_encontrado
from app.domain.services.apellido_extranjero import apellido_extranjero
from app.api.exceptions.apellido_exceptions import ApellidoInvalidoError


class ObtenerApellidoIA:
    def __init__(self, apellido_normalizado: str, apellido_original: str):
        self.apellido_normalizado = apellido_normalizado
        self.apellido_original = apellido_original

    def ejecutar(self) -> Dict:
        ai_response = generar_apellido_ia(self.apellido_normalizado)
        
        if ai_response:
            self._validar_ai_response(ai_response)

            if not ai_response['es_apellido_real']:
                raise ApellidoInvalidoError(
                    f"Error al digitar el apellido. {self.apellido_original} no es un apellido válido."
                )
            
            if ai_response['es_apellido_extranjero']:
                return apellido_extranjero()

            apellido_obj = self._crear_apellido(ai_response)

            distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
            frases = Frases.objects.filter(apellido=apellido_obj)

            return {
                "estado": "encontrado",
                "fuente": apellido_obj.fuente,
                "apellido_original": self.apellido_original,
                "apellido_normalizado": apellido_obj.apellido,
                "distribuciones": distribuciones,
                "frases": frases
            }
        else:
            return apellido_no_encontrado()
        
    def _validar_ai_response(self, ai_response: Dict):
        try:
            validate(instance=ai_response, schema=AI_APELLIDO_DISTRO_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"Error al validar la respuesta del AI: {e}")

    def _crear_apellido(self, ai_response: Dict) -> Apellido:
        REGIONES = {
            "Huila": "Uno de los principales productores nacionales.",
            "Nariño": "Perfiles dulces y aromáticos.",
            "Antioquia": "Conocido por su cuerpo y balance",
            "Santander": "Con notas herbales y aroma pronunciado.",
            "Cauca": "Sabores complejos y equilibrados.",
            "Valle del Cauca": "Perfiles con carácter.",
            "Caldas": "Parte del paisaje Cultural Cafetero.",
            "Tolima": "Suave y balanceado.",
            "Sierra Nevada": "Intensidad y notas unicas de esta región.",
            "Boyacá": "Por definir.",
            "La Guajira": "Con matices cítricos y refrescantes.",
            "Risaralda": "Equilibrio y notas frutales.",
            "Cundinamarca": "Perfil característico de su región cafetera.",
            "Cesar": "Café con notas dulces y balanceadas.",
            "Quindío": "Parte del Eje Cafetero con aroma y suavidad destacada.",
        }

        with transaction.atomic():
            apellido_obj, _ = Apellido.objects.get_or_create(
                apellido=ai_response['apellido'],
                defaults={'fuente': 'IA Gemini'}
            )

            for dist in ai_response['distribuciones']:
                departamento, _ = Departamento.objects.get_or_create(
                    nombre=dist['departamento'],
                    frase=REGIONES[dist['departamento']]
                )
                DistribucionApellidoDepartamento.objects.get_or_create(
                    apellido=apellido_obj,
                    departamento=departamento,
                    defaults={
                        'porcentaje': dist['porcentaje'],
                        'ranking': dist['ranking'],
                    }
                )

            for frase in ai_response['frases']:
                Frases.objects.get_or_create(
                    categoria=frase['categoria'],
                    frase=frase['texto'],
                    apellido=apellido_obj,
                )

            return apellido_obj
        