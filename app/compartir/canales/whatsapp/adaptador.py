from abc import ABC, abstractmethod


class WhatsappAdaptador(ABC):

    @abstractmethod
    def enviar_mensaje(self, para: str, cuerpo: str) -> str:
        """
        Envía mensajes y devuelve un 'provider_message_id'
        Lanza excepción si falla.
        """
        pass