from typing import Dict
from jsonschema import validate, ValidationError
from django.db import transaction

from app.domain.models.apellido_models import (
    Apellido,
    Departamento,
    DistribucionApellidoDepartamento,
    Frases
)

from app.integrations.ai_cliente import generar_apellido_ia
from app.schemas.ai_apellido_distro_schema import AI_APELLIDO_DISTRO_SCHEMA
from app.domain.services.casos_especiales import apellido_extranjero
from app.api.exceptions.apellido_exceptions import ApellidoInvalidoError
from app.utils.constantes import REGIONES


class ServicioIA:
    def __init__(self, apellido_normalizado: str, apellido_original: str):
        self.apellido_normalizado = apellido_normalizado
        self.apellido_original = apellido_original

    def ejecutar(self) -> Dict:
        ai_response = generar_apellido_ia(self.apellido_original)
        
        self._validar_ai_response(ai_response)

        if not ai_response['es_apellido_real']:
            raise ApellidoInvalidoError(
                f"Error al digitar el apellido. {self.apellido_original} no es un apellido válido."
            )
        
        if ai_response['es_apellido_extranjero']:
            return apellido_extranjero(self.apellido_original, self.apellido_normalizado)

        apellido_obj = self._crear_apellido(ai_response)

        distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
        frases = Frases.objects.filter(apellido=apellido_obj)

        return {
            "estado": "encontrado",
            "fuente": apellido_obj.fuente,
            "apellido_original": self.apellido_original,
            "apellido_normalizado": apellido_obj.apellido,
            "distribuciones": list(distribuciones),
            "frases": list(frases)
        }
        
    def _validar_ai_response(self, ai_response: Dict):
        try:
            validate(instance=ai_response, schema=AI_APELLIDO_DISTRO_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"Error al validar la respuesta del AI: {e}")

    def _crear_apellido(self, ai_response: Dict) -> Apellido:
        with transaction.atomic():
            apellido_obj, created = Apellido.objects.get_or_create(
                apellido=self.apellido_normalizado,
                defaults={'estado': Apellido.PENDIENTE, 'fuente': 'IA Gemini'}
            )

            if not created:
                apellido_obj.fuente = 'IA Gemini'
                apellido_obj.es_inferido = True

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

            apellido_obj.estado = Apellido.LISTO
            apellido_obj.save()

            return apellido_obj

    def _marcar_como_fallido(self):
        apellido_obj = Apellido.objects.filter(apellido=self.apellido_normalizado).first()
        if apellido_obj:
            apellido_obj.estado = Apellido.FALLIDO
            apellido_obj.save()
