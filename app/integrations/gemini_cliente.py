import json, os

from typing import Dict
from google import genai

from app.utils.constantes import REGIONES
from app.api.exceptions.apellido_exceptions import IntegracionIAError


# Formatear REGIONES para una mejor lectura por la IA
REGIONES_STR = "\n".join([f"- {depto}: {desc}" for depto, desc in REGIONES.items()])

SYSTEM_INSTRUCTION = f"""
Eres un experto en genealogía cafetera de Juan Valdez. Tu tarea es analizar apellidos colombianos y generar datos demográficos y creativos.

REGLAS DE VALIDACIÓN:
- Si el término es texto aleatorio, sin sentido o un insulto: 'es_apellido_real' = false, arreglos vacíos.
- Si el término es un apellido extranjero (ej. Smith, Johnson): 'es_apellido_extranjero' = true, arreglos vacíos.

REFERENCIA DE REGIONES (Solo usa estas):
{REGIONES_STR}

INSTRUCCIONES DE GENERACIÓN:
1. Solo si 'es_apellido_real' es true.
2. Suma de porcentajes siempre 100%.
3. Ranking aleatorio entre 1 y 100.
4. Generar exactamente 4 frases: 
   - 1 de 'PERSONALIDAD' (historia/ímpetu).
   - 3 de 'SABORES' (metáforas cafeteras/gastronómicas de la región de origen). La frase debe incluir el apellido.
"""


class GeminiIACliente:
    def __init__(self, schema: Dict):
        try:
            # Configuración de tiempo de espera de 30 segundos (30,000 ms)
            http_options = {"timeout": 30000}
            self.cliente = genai.Client(http_options=http_options)
        except ValueError as e:
            raise IntegracionIAError(f"Error de configuración de la IA: {str(e)}")
        
        self.config_generacion = {
            "response_mime_type": "application/json",
            "response_schema": schema,
            "temperature": 0.1,
            "system_instruction": SYSTEM_INSTRUCTION
        }

    def obtener_apellido_distribuciones(self, apellido: str) -> Dict:
        prompt = f"Analiza el apellido: '{apellido}'"
        return self.ejecutar_modelo(prompt)

    def obtener_frases_batch(self, apellidos_con_dist: list) -> Dict:
        """
        Obtiene frases para múltiples apellidos en una sola llamada.
        apellidos_con_dist: list de dicts {"apellido": str, "distribuciones": dict}
        """
        items_desc = []
        for item in apellidos_con_dist:
            items_desc.append(f"Apellido: {item['apellido']}, Distribuciones: {item['distribuciones']}")
        
        prompt = "Genera frases para estos apellidos:\n" + "\n".join(items_desc)
        return self.ejecutar_modelo(prompt)

    def ejecutar_modelo(self, prompt: str):
        try:
            response = self.cliente.models.generate_content(
                model=os.environ.get('GEMINI_MODELO'),
                contents=prompt,
                config=self.config_generacion
            )

            resultado = json.loads(response.text)
            
            return resultado
        except Exception as e:
            raise IntegracionIAError(f"Fallo al ejecutar el modelo de IA: {str(e)}")
