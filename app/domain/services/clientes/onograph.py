import requests, os
from typing import Dict, Optional, Any

from app.utils.math import ajustar_porcentaje
from app.utils.constantes import REGIONES, REGION_GENERICA, FRASES_GENERICAS
from app.api.exceptions.apellido_exceptions import ExternalAPIError


class ServicioOnograph:
    def __init__(self, apellido_normalizado: str, apellido_original: str):
        self.apellido_normalizado = apellido_normalizado
        self.apellido_original = apellido_original

    def _peticion_api(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
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

    def _preparar_parametros(self) -> tuple[str, Dict[str, Any]]:
        URL = os.environ.get('URL_ONOGRAPH')
        API_KEY = os.environ.get('API_KEY_ONOGRAPH')
        
        PARAMETROS = {
            'key': API_KEY,
            'name': self.apellido_original,
            'type': 'surname',
            'jurisdiction': 'co',
        }
        return URL, PARAMETROS

    def _procesar_jurisdicciones(self, response: Dict[str, Any]) -> list[Dict[str, Any]]:
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
        return distribuciones

    def _aplicar_estadisticas(self, distribuciones: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        total_incidencia = sum(d['incidencia'] for d in distribuciones)
        if total_incidencia > 0:
            for d in distribuciones:
                d['porcentaje'] = round((d['incidencia'] * 100) / total_incidencia)
        else:
            for d in distribuciones:
                d['porcentaje'] = 0
        
        # Ajustar porcentajes para que sumen 100%
        return ajustar_porcentaje(distribuciones)

    def ejecutar(self) -> Optional[Dict[str, Any]]:
        """
        Ejecuta la petición a la API de Onograph y retorna los datos en memoria.
        """
        URL, PARAMETROS = self._preparar_parametros()
        response = self._peticion_api(URL, PARAMETROS)

        # Validamos que la respuesta contenga datos
        if 'jurisdictions' not in response:
            return {
                "estado": "no_encontrado",
                "mensaje": "No se pudo obtener datos de la API"
            }
        
        # Construimos la lista de distribuciones si la respuesta es exitosa
        distribuciones = self._procesar_jurisdicciones(response)
        
        frases = []

        # Si no hay distribuciones en las regiones definidas, aplicamos fallback genérico
        if not distribuciones:
            distribuciones = REGION_GENERICA
            frases = FRASES_GENERICAS
        else:
            distribuciones = self._aplicar_estadisticas(distribuciones)

        return {
            "estado": "encontrado",
            "fuente": 'https://forebears.io',
            "apellido_original": self.apellido_original,
            "apellido_normalizado": self.apellido_normalizado,
            "distribuciones": distribuciones,
            "frases": frases,
            "nuevo": True # Flag para indicar que necesita persistencia
        }
