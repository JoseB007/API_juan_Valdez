from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from ..entidades import ResultadoEnvio, EstadoEnvio


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
            raise e