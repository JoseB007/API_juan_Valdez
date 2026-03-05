import os
from typing import Dict
from abc import abstractmethod

from .adaptadorIA import AdaptadorIA
from .groq_cliente import GroqIACliente
from .gemini_cliente import GeminiIACliente
from app.api.exceptions.apellido_exceptions import IntegracionIAError


class IAFactory:
    _MAPA_PROVEEDORES = {
        "groq": GroqIACliente,
        "gemini": GeminiIACliente,
        # "anthropic": AnthropicClienteIA,
    }

    @abstractmethod
    def obtener_cliente(schema: Dict) -> AdaptadorIA:
        try:
            # 1. Leer variables de entorno
            proveedor = os.environ.get("IA_PROVEEDOR", "GROQ").lower()
            api_key = os.environ.get("IA_API_KEY")
            modelo = os.environ.get("IA_MODELO")

            # 2. Buscar la clase correspondiente en el mapa
            cliente = IAFactory._MAPA_PROVEEDORES.get(proveedor)

            # 3. Retornar la instancia configurada
            return cliente(api_key=api_key, modelo=modelo, schema=schema)
        
        except Exception as e:
            raise IntegracionIAError(f"Error al inicializar el adaptador: {proveedor} -> {str(e)}")