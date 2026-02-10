from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from enum import Enum
from dataclasses import dataclass


class EstadoEnvio(Enum):
    ACEPTADO = "ACEPTADO"
    FALLIDO = "FALLIDO"


@dataclass
class ResultadoEnvio:
    estado: EstadoEnvio
    canal: str
    mensaje: str


class EnviadorCorreo:
    def enviar(self, asunto: str, cuerpo: str, destinatario: str, cuerpo_html: str = None):
        try:
            email = EmailMultiAlternatives(
                subject=asunto,
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario],
            )
            if cuerpo_html:
                email.attach_alternative(cuerpo_html, "text/html")
            email.send()

            return ResultadoEnvio(
                estado=EstadoEnvio.ACEPTADO,
                canal="email",
                mensaje="Correo enviado correctamente."
            )
        except Exception as e:
            return ResultadoEnvio(
                estado=EstadoEnvio.FALLIDO,
                canal="email",
                mensaje=f"Error de servidor al enviar el correo. {e}"
            )