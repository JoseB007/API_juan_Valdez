import os, requests, logging

from .adaptador import WhatsappAdaptador
from .exceptions import (
    WhatsappAuthError, 
    WhatsappValidationError, 
    WhatsappRateLimitError, 
    WhatsappProviderError,
    WhatsappError
)

logger = logging.getLogger(__name__)


class MetaAdaptador(WhatsappAdaptador):

    def enviar_mensaje(self, para: str, cuerpo: str) -> str:
        # La API de Meta requiere el ID del Phone Number y un Access Token (Bearer)
        access_token = os.environ.get('META_ACCESS_TOKEN')
        phone_number_id = os.environ.get('META_PHONE_NUMBER_ID')
        
        # URL de Meta Graph API
        url_base = os.environ.get('META_API_URL', 'https://graph.facebook.com/v21.0')
        url = f'{url_base}/{phone_number_id}/messages'

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Estructura de mensajes de Meta
        data = {
            "messaging_product": "whatsapp",
            "to": para,
            "type": "text",
            "text": {
                "body": cuerpo
            }
        }

        try:
            response = requests.post(
                url=url,
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code >= 400:
                self._manejar_error_http(response)
            

            return response.json()['messages'][0]['id']

        except requests.Timeout:
            logger.error(f"Timeout al enviar mensaje via Meta a {para}")
            raise WhatsappProviderError("Timeout de conexión con Meta", status_code=408)
        except requests.RequestException as e:
            logger.error(f"Error de red con Meta: {str(e)}")
            raise WhatsappError(f"Error de conexión con Meta: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Respuesta inesperada de Meta. Error: {str(e)}")
            raise WhatsappProviderError(f"Respuesta inesperada del proveedor: {str(e)}")

    def _manejar_error_http(self, response: requests.Response):
        """Mapea errores HTTP de Meta a excepciones personalizadas."""
        status_code = response.status_code
        error_data = response.json().get('error', {})
        mensaje_error = error_data.get('message', 'Sin mensaje de error detallado')
        
        logger.error(f"Error de Meta API ({status_code}): {mensaje_error}")

        if status_code in [401, 403]:
            raise WhatsappAuthError(f"Error de autenticación/permisos: {mensaje_error}", status_code=status_code)
        elif status_code == 400:
            raise WhatsappValidationError(f"Datos del mensaje inválidos: {mensaje_error}", status_code=status_code)
        elif status_code == 429:
            raise WhatsappRateLimitError(f"Límite de velocidad excedido: {mensaje_error}", status_code=status_code)
        elif status_code >= 500:
            raise WhatsappProviderError(f"Error interno de Meta: {mensaje_error}", status_code=status_code)
        else:
            raise WhatsappError(f"Error de Meta: {mensaje_error}", status_code=status_code)
