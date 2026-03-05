import json

from groq import Groq

from .adaptadorIA import AdaptadorIA
from .utils import SYSTEM_INSTRUCTION


class GroqIACliente(AdaptadorIA):

    def _configurar_cliente(self) -> Groq:
        return Groq(api_key=self.api_key)
    
    def _ejecutar_modelo(self, prompt: str):
        response = self.cliente.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"{prompt}\n\nResponde siguiendo este esquema JSON: {json.dumps(self.schema)}"}
            ],
            model=self.modelo,
            response_format={'type': 'json_object'},
            temperature=0.1,
        )

        contenido = response.choices[0].message.content
        return json.loads(contenido)


