from typing import Dict, Any
from abc import ABC, abstractmethod

from app.api.exceptions.apellido_exceptions import IntegracionIAError


class AdaptadorIA(ABC):
    def __init__(self, api_key: str, modelo: str, schema: Dict):
        self.api_key = api_key
        self.modelo = modelo
        self.schema = schema
        self.cliente = self._configurar_cliente()

    @abstractmethod
    def _configurar_cliente(self) -> Any:
        pass

    @abstractmethod
    def _ejecutar_modelo(self, prompt: str):
        pass

    def ejecutar(self, prompt: str):
        try:
            return self._ejecutar_modelo(prompt)
        except Exception as e:
            raise IntegracionIAError(f"Error en {self.modelo}: {e}")
        
