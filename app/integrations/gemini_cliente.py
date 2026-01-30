import json

from typing import Dict
from google import genai

from app.schemas.ai_response_schema import AI_RESPONSE_SCHEMA


class GeminiIACliente:
    def __init__(self):
        self.cliente = genai.Client()
        self.config_generacion = {
            "response_mime_type": "application/json",
            "response_schema": AI_RESPONSE_SCHEMA,
            "temperature": 0.1,
        }

    def obtener_apellido(self, apellido: str) -> Dict:
        prompt = self._ai_prompt(apellido)

        try:
            response = self.cliente.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=self.config_generacion
            )

            return json.loads(response.text)
        except Exception as e:
            print(f"Error al consultar GeminiAI: {e}")
            return None
        
    def _ai_prompt(self, apellido: str):
        return f"""
        Genera estadísticas demográficas para el apellido '{apellido}' en Colombia.
        
        Instrucciones para las 'frases':
        1. La primera frase debe ser de la categoría 'PERSONALIDAD'.
        2. Las 3 frases restantes deben ser de la categoría 'SABORES'.
        """

# class GeminiIACliente:
#     def __init__(self):
#         self.cliente = genai.Client()

#     def obtener_apellido(self, apellido: str) -> Dict:
#         prompt = self._ai_prompt(apellido)

#         try:
#             response = self.cliente.models.generate_content(
#                 model="gemini-3-flash-preview",
#                 contents=prompt
#             )

#             contenido = response.text

#             return json.loads(contenido)
#         except Exception as e:
#             print(f"Error al consultar GeminiAI: {e}")
#             return None
        
#     def _ai_prompt(self, apellido: str):
#         return f"""
#         Inferir estadísticas de apellidos para Colombia.

#         Apellido: {apellido}
#         Lenguaje: Español

#         Reglas:
#         - Devolver SOLO JSON
#         - Reducir la confianza si no hay certeza

#         JSON estructura: {AI_RESPONSE_SCHEMA}
#         """