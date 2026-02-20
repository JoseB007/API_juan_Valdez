import os, requests, logging
from requests.auth import HTTPBasicAuth

from .adaptador import WhatsappAdaptador
from .exceptions import (
    WhatsappAuthError, 
    WhatsappValidationError, 
    WhatsappRateLimitError, 
    WhatsappProviderError,
    WhatsappError
)

logger = logging.getLogger(__name__)


class TwilioAdaptador(WhatsappAdaptador):

    def enviar_mensaje(self, para: str, cuerpo: str) -> str:
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        whatsapp_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')

        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'

        data = {
            "From": whatsapp_number,
            "To": f"whatsapp:{para}",
            "Body": cuerpo,
        }

        try:
            response = requests.post(
                url=url,
                data=data,
                auth=HTTPBasicAuth(account_sid, auth_token),
                timeout=10
            )

            if response.status_code >= 400:
                self._manejar_error_http(response)

            return response.json()['sid']

        except requests.Timeout:
            logger.error(f"Timeout al enviar mensaje via Twilio a {para}")
            raise WhatsappProviderError("Timeout de conexión con Twilio", status_code=408)
        except requests.RequestException as e:
            logger.error(f"Error de red con Twilio: {str(e)}")
            raise WhatsappError(f"Error de conexión con Twilio: {str(e)}")
        except (KeyError, ValueError) as e:
            logger.error(f"Respuesta inesperada de Twilio: {response.text}")
            raise WhatsappProviderError(f"Respuesta inesperada del proveedor: {str(e)}")

    def _manejar_error_http(self, response: requests.Response):
        """Mapea errores HTTP de Twilio a excepciones personalizadas."""
        status_code = response.status_code
        try:
            error_data = response.json()
            mensaje_error = f"{error_data.get('message', response.text)} (Code: {error_data.get('code')})"
        except Exception:
            mensaje_error = response.text

        logger.error(f"Error de Twilio API ({status_code}): {mensaje_error}")

        if status_code in [401, 403]:
            raise WhatsappAuthError(f"Error de autenticación: {mensaje_error}", status_code=status_code)
        elif status_code == 400:
            raise WhatsappValidationError(f"Datos inválidos: {mensaje_error}", status_code=status_code)
        elif status_code == 429:
            raise WhatsappRateLimitError(f"Límite excedido: {mensaje_error}", status_code=status_code)
        elif status_code >= 500:
            raise WhatsappProviderError(f"Error del proveedor Twilio: {mensaje_error}", status_code=status_code)
        else:
            raise WhatsappError(f"Error de Twilio: {mensaje_error}", status_code=status_code)
