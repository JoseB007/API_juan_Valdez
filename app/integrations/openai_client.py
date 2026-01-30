import json, os
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

from app.schemas.ai_response_schema import AI_RESPONSE_SCHEMA


class OpenAICliente:
    def __init__(self):
        api_key = os.environ.get('OPENAI_API_KEY')
        self.cliente = OpenAI(api_key=api_key)

    def obtener_apellido(self, apellido: str) -> Dict:
        prompt = self._ai_prompt(apellido)

        try:
            response = self.cliente.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un asistente útil."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            contenido = response.choices[0].message.content

            return json.load(contenido)
            
        except Exception as e:
            print(f"Error al consultar OpenAI: {e}")
            return None

    def _ai_prompt(self, apellido: str):
        return f"""
        Inferir estadísticas de apellidos para Colombia.

        Apellido: {apellido}
        Lenguaje: Español

        Reglas:
        - Devolver SOLO JSON
        - Reducir la confianza si no hay certeza

        JSON structure: {AI_RESPONSE_SCHEMA}
        """