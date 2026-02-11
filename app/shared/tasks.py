from celery import shared_task
from .email_sender import EnviadorCorreo


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    retry_jitter=True
)
def tarea_compartir_email(asunto: str, cuerpo: str, destinatario: str, cuerpo_html: str = None):
    enviador = EnviadorCorreo()
    enviador.enviar(
        asunto=asunto,
        cuerpo=cuerpo,
        destinatario=destinatario,
        cuerpo_html=cuerpo_html,
    )
    return {
        "estado": "ENVIADO",
        "destinatario": destinatario,
    }
