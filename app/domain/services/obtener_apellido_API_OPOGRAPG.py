import requests, os, json
from typing import Dict, Optional, Any

from django.db import transaction

from app.integrations.ai_cliente import obtener_frases_ai
from app.domain.models.models import (
    Apellido,
    Departamento,
    DistribucionApellidoDepartamento,
    Frases
)
from app.domain.services.apellido_no_encontrado import apellido_no_encontrado


class ObtenerApellidoAPIOpograph:
    def __init__(self, apellido_normalizado: str, apellido_original: str):
        self.apellido_normalizado = apellido_normalizado
        self.apellido_original = apellido_original

    def peticion_api(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Realiza la petición a la API de Onograph. Retorna la respuesta en formato JSON.
        """
        try:
            response = requests.get(url, params=params, timeout=10)
            
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error inesperado: {e}")
        
        return None

    def obtener_frases_ia(self, distribuciones: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Obtiene las frases relacionadas con el apellido.
        """
        ia_response = obtener_frases_ai(self.apellido_normalizado, distribuciones)

        if not ia_response:
            return None

        return ia_response
    
    def generar_apellido_distribuciones(self, distribuciones: Dict[str, Any]) -> Dict[str, Any]:
        frases = self.obtener_frases_ia(distribuciones)

        with transaction.atomic():
            apellido_obj, _ = Apellido.objects.get_or_create(
                apellido=self.apellido_normalizado,
                defaults={'origen': 'REAL'}
            )

            for dist in distribuciones:
                departamento_obj, _ = Departamento.objects.get_or_create(
                    nombre=dist['departamento']
                )
                DistribucionApellidoDepartamento.objects.get_or_create(
                    apellido=apellido_obj,
                    departamento=departamento_obj,
                    defaults={
                        'porcentaje': dist['porcentaje'],
                        'ranking': dist['ranking'],
                        'origen': 'IA'
                    }
                )

            for frase in frases['frases']:
                Frases.objects.get_or_create(
                    apellido=apellido_obj,
                    categoria=frase['categoria'],
                    frase=frase['texto'],
                    defaults={'origen': 'IA'}
                )

            distribuciones_apellido = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
            frases = Frases.objects.filter(apellido=apellido_obj)

            return {
                "estado": "encontrado",
                "origen": apellido_obj.origen,
                "apellido_original": self.apellido_original,
                "apellido_normalizado": apellido_obj.apellido,
                "departamentos": distribuciones_apellido,
                "frases": frases
            }

    def ejecutar(self) -> Optional[Dict[str, Any]]:
        """
        Ejecuta la petición a la API de Onograph.
        """
        URL = 'https://ono.4b.rs/v1/jur'
        API_KEY = os.environ.get('API_KEY_ONOGRAPH')
        
        PARAMETROS = {
            'key': API_KEY,
            'name': self.apellido_normalizado,
            'type': 'surname',
            'jurisdiction': 'co',
            # 'limit': 3
        }

        response = self.peticion_api(URL, PARAMETROS)

        # Validamos que la respuesta sea exitosa y contenga datos
        if not response or 'jurisdictions' not in response:
            return {
                "estado": "error",
                "mensaje": "No se pudo obtener datos de la API"
            }
        
        REGIONES = {
            "Huila",
            "Nariño",
            "Antioquia",
            "Santander",
            "Cauca",
            "Valle del Cauca",
            "Caldas",
            "Tolima",
            "Sierra Nevada",
            "Boyacá",
            "La Guajira",
            "Risaralda",
            "Cundinamarca",
            "Cesar",
            "Quindío",
        }

        # Construimos la lista de distribuciones si la respuesta es exitosa
        distribuciones = [
            {
                "incidencia": depart.get('incidence'),
                "ranking": depart.get('rank', 0),
                "departamento": depart.get('jurisdiction', 'Desconocido').split(" Department")[0].strip()
            }
            for depart in response.get('jurisdictions', []) if depart['jurisdiction'].split(" Department")[0] in REGIONES
        ][:3]

        total_incidencia = sum(d['incidencia'] for d in distribuciones)

        if total_incidencia > 0:
            for d in distribuciones:
                d['porcentaje'] = (d['incidencia'] * 100) / total_incidencia
        else:
            for d in distribuciones:
                d['porcentaje'] = 0
        
        return self.generar_apellido_distribuciones(distribuciones)