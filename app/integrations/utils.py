from typing import Dict, List
from app.utils.constantes import REGIONES


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

IMPORTANTE: Responde siempre en formato JSON válido según el esquema proporcionado.
"""

def obtener_apellido_distribuciones(apellido: str) -> Dict:
    prompt = f"Analiza el apellido: '{apellido}'"
    return prompt

def obtener_frases_batch(apellidos_con_dist: List[Dict]) -> Dict:
    """
    Obtiene frases para múltiples apellidos en una sola llamada.
    apellidos_con_dist: list de dicts {"apellido": str, "distribuciones": dict}
    """
    items_desc = []
    for item in apellidos_con_dist:
        items_desc.append(f"Apellido: {item['apellido']}, Distribuciones: {item['distribuciones']}")
    
    prompt = "Genera frases para estos apellidos:\n" + "\n".join(items_desc)
    return prompt

