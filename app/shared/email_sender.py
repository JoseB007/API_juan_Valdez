from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class EmailSender:
    def _send(self, asunto: str, cuerpo: str, destinatario: str):
        try:
            email = EmailMultiAlternatives(
                subject=asunto,
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario],
            )
            email.send()
        except Exception as e:
            print(f"Error enviando correo: {e}")