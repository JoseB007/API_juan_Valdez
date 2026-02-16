from celery import shared_task
from celery.utils.log import get_task_logger
from .email_sender import EnviadorCorreo

logger = get_task_logger(__name__)

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    retry_jitter=True
)
def tarea_compartir_email(asunto: str, cuerpo: str, destinatario: str, cuerpo_html: str = None):
    try:
        enviador = EnviadorCorreo()
        enviador.enviar(
            asunto=asunto,
            cuerpo=cuerpo,
            destinatario=destinatario,
            cuerpo_html=cuerpo_html,
        )
        logger.info(f"Email enviado exitosamente a {destinatario}")
        return {
            "estado": "ENVIADO",
            "destinatario": destinatario,
        }
    except Exception as e:
        logger.error(f"Error al enviar email a {destinatario}: {str(e)}")
        raise e
