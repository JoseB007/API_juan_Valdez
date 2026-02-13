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


class ObtenerApellidoAPIOnograph:
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
        ia_response = generar_frases_ia(self.apellido_original, distribuciones)

        if not ia_response:
            return None

        return ia_response
    
    def generar_apellido_distribuciones(self, distribuciones: Dict[str, Any]) -> Dict[str, Any]:
        frases = self.obtener_frases_ia(distribuciones)

        with transaction.atomic():
            apellido_obj, created = Apellido.objects.get_or_create(
                apellido=self.apellido_normalizado,
                defaults={'estado': Apellido.PENDIENTE, 'fuente': 'https://forebears.io'}
            )

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
                "distribuciones": distribuciones_apellido,
                "frases": frases_obj
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
                d['porcentaje'] = (d['incidencia'] * 100) / total_incidencia
        else:
            for d in distribuciones:
                d['porcentaje'] = 0
        
        return self.generar_apellido_distribuciones(distribuciones)