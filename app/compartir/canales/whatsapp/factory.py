import os
from .twilio import TwilioAdaptador
from .meta import MetaAdaptador

def get_whatsapp_adaptador():
    proveedor = os.environ.get('WHATSAPP_PROVIDER')
    if proveedor == "twilio":
        return TwilioAdaptador()
    elif proveedor == "meta":
        return MetaAdaptador()
    else:
        raise ValueError("Proveedor de WhatsApp no soportado")
