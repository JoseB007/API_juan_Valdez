import json

from typing import Dict
from google import genai


class GeminiIACliente:
    def __init__(self, schema: Dict):
        self.cliente = genai.Client()
        self.config_generacion = {
            "response_mime_type": "application/json",
            "response_schema": schema,
            "temperature": 0.1,
        }

    def obtener_apellido_distribuciones(self, apellido: str) -> Dict:
        prompt = self._ai_prompt_apellido(apellido)

        return self.ejecutar_modelo(prompt)
        
    def obtener_frases_apellido(self, apellido: str, dist: Dict) -> Dict:
        prompt = self._ai_prompt_frases_apellido(apellido, dist)

        return self.ejecutar_modelo(prompt)

    def ejecutar_modelo(self, prompt: str):
        try:
            response = self.cliente.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=self.config_generacion
            )

            resultado = json.loads(response.text)
            
            return resultado
        except Exception as e:
            return None
        
    def _ai_prompt_apellido(self, apellido: str):
        return f"""
        Analiza el término '{apellido}'. 

        TAREA DE VALIDACIÓN:
        - Si el término es texto aleatorio (ej. 'asdfg'), una combinación sin sentido de letras, o un insulto, establece 'es_apellido_real' en false y deja los arrays de 'distribuciones' y 'frases' vacíos.
        - Si el término es un apellido extranjero (ej. 'Smith', 'Johnson', 'Williams', 'Brown', 'Jones'), establece 'es_apellido_extranjero' en true y deja los arrays de 'distribuciones' y 'frases' vacíos.
        
        
        TAREA DE GENERACIÓN (Solo si 'es_apellido_real' es true):
        1. Genera estadísticas demográficas para el apellido '{apellido}' en Colombia.
        2. Genera 4 frases obligatorias:
            - La primera: Categoría 'PERSONALIDAD' (relacionada con el ímpetu o historia del apellido).
            - Las otras tres: Categoría 'SABORES' (metáforas gastronómicas sobre el café, derivados y relacionados propios de la región de origen).
        """

    def _ai_prompt_frases_apellido(self, apellido: str, distribuciones: Dict):
        return f"""
        Analiza el término '{apellido}' y las distribuciones por departamento de ese apellido: '{distribuciones}'. 
        
        TAREA DE GENERACIÓN:
        1. Genera 4 frases obligatorias:
            - La primera: Categoría 'PERSONALIDAD' (relacionada con el ímpetu o historia del apellido).
            - Las otras tres: Categoría 'SABORES' (metáforas gastronómicas sobre el café, derivados y relacionados propios de la región de origen).
        """