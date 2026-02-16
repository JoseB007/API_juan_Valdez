import requests, os
from typing import Dict, Optional, Any

from django.db import transaction

from app.integrations.ai_cliente import generar_frases_ia
from app.domain.models.models import (
    Apellido,
    Departamento,
    DistribucionApellidoDepartamento,
    Frases
)
from app.utils.math import ajustar_porcentaje
from app.utils.constantes import REGIONES
from app.api.exceptions.apellido_exceptions import ExternalAPIError


class ObtenerApellidoAPIOnograph:
    def __init__(self, apellido_normalizado: str, apellido_original: str):
        self.apellido_normalizado = apellido_normalizado
        self.apellido_original = apellido_original

    def peticion_api(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza la petición a la API de Onograph. Retorna la respuesta en formato JSON.
        """
        try:
            response = requests.get(url, params=params, timeout=10)
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'status' in data:
                for status_item in data['status']:
                    if status_item.get('type') == 'error':
                        raise ExternalAPIError(status_item.get('message', 'Error desconocido en la API externa'))
            
            return data
        except requests.exceptions.HTTPError as e:
            raise ExternalAPIError(f"Error de la API externa (HTTP {e.response.status_code})")
        except ExternalAPIError:
            raise
        except Exception as e:
            raise ExternalAPIError(f"Error inesperado al conectar con la API: {str(e)}")

    def obtener_frases_ia(self, distribuciones: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene las frases relacionadas con el apellido.
        """
        return generar_frases_ia(self.apellido_original, distribuciones)
    
    def generar_apellido_distribuciones(self, distribuciones: Dict[str, Any]) -> Dict[str, Any]:
        with transaction.atomic():
            apellido_obj, created = Apellido.objects.get_or_create(
                apellido=self.apellido_normalizado,
                defaults={'estado': Apellido.PENDIENTE, 'fuente': 'https://forebears.io'}
            )

            # Verificar si ya existen frases para este apellido, si no es así se procede
            # a llamar a la IA para generarlas
            frases_existentes = Frases.objects.filter(apellido=apellido_obj).exists()
            
            frases = None
            if not frases_existentes:
                frases = self.obtener_frases_ia(distribuciones)

            if not created:
                apellido_obj.fuente = 'https://forebears.io'

            for dist in distribuciones:
                departamento_obj, _ = Departamento.objects.get_or_create(
                    nombre=dist['departamento']['nombre'],
                    frase=dist['departamento']['frase']
                )
                DistribucionApellidoDepartamento.objects.get_or_create(
                    apellido=apellido_obj,
                    departamento=departamento_obj,
                    defaults={
                        'porcentaje': dist['porcentaje'],
                        'ranking': dist['ranking'],
                    }
                )

            if frases and 'frases' in frases:
                for frase in frases['frases']:
                    Frases.objects.get_or_create(
                        categoria=frase['categoria'],
                        frase=frase['texto'],
                        apellido=apellido_obj,
                    )

            apellido_obj.estado = Apellido.LISTO
            apellido_obj.save()

            distribuciones_apellido = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
            frases_obj = Frases.objects.filter(apellido=apellido_obj)

            return {
                "estado": "encontrado",
                "fuente": apellido_obj.fuente,
                "apellido_original": self.apellido_original,
                "apellido_normalizado": apellido_obj.apellido,
                "distribuciones": list(distribuciones_apellido),
                "frases": list(frases_obj)
            }

    def ejecutar(self) -> Optional[Dict[str, Any]]:
        """
        Ejecuta la petición a la API de Onograph.
        """
        URL = 'https://ono.4b.rs/v1/jur'
        API_KEY = os.environ.get('API_KEY_ONOGRAPH')
        
        PARAMETROS = {
            'key': API_KEY,
            'name': self.apellido_original,
            'type': 'surname',
            'jurisdiction': 'co',
            # 'limit': 3
        }

        response = self.peticion_api(URL, PARAMETROS)

        # Validamos que la respuesta contenga datos
        if 'jurisdictions' not in response:
            return {
                "estado": "no_encontrado",
                "mensaje": "No se pudo obtener datos de la API"
            }
        
        # Construimos la lista de distribuciones si la respuesta es exitosa
        distribuciones = []

        for depart in response.get('jurisdictions', []):
            nombre_depart_api = depart.get('jurisdiction').split(" Department")[0].strip()

            if nombre_depart_api in REGIONES:
                distribuciones.append({
                    "incidencia": depart.get('incidence'),
                    "ranking": depart.get('rank', 0),
                    "departamento": {
                        "nombre": nombre_depart_api,
                        "frase": REGIONES[nombre_depart_api]
                    },
                })
                

            if len(distribuciones) == 3:
                break
        total_incidencia = sum(d['incidencia'] for d in distribuciones)

        if total_incidencia > 0:
            for d in distribuciones:
                d['porcentaje'] = round((d['incidencia'] * 100) / total_incidencia)
        else:
            for d in distribuciones:
                d['porcentaje'] = 0
        
        # Ajustar porcentajes para que sumen 100%
        distribuciones = ajustar_porcentaje(distribuciones)
        
        return self.generar_apellido_distribuciones(distribuciones)