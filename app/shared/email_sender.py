from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from enum import Enum
from dataclasses import dataclass


class EstadoCompartido(Enum):
    ACEPTADO = "ACEPTADO"
    FALLIDO = "FALLIDO"


@dataclass
class ResultadoCompartido:
    estado: EstadoCompartido
    canal: str
    mensaje: str


class EmailSender:
    def send(self, asunto: str, cuerpo: str, destinatario: str):
        try:
            email = EmailMultiAlternatives(
                subject=asunto,
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario],
            )
            email.send()

            return ResultadoCompartido(
                estado=EstadoCompartido.ACEPTADO,
                canal="email",
                mensaje="Correo enviado correctamente."
            )
        except Exception as e:
            return ResultadoCompartido(
                estado=EstadoCompartido.FALLIDO,
                canal="email",
                mensaje=f"Error al enviar el correo. {e}"
            )