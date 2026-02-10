from typing import Dict

from .generar_mensaje import GeneradorMensaje
from .email_sender import ResultadoEnvio, EstadoEnvio
from .tasks import tarea_compartir_email
from ..domain.models.models import DistribucionApellidoDepartamento, Apellido


class ServicioCompartir:
    def __init__(self, apellido: str, canal: str, destinatario: str):
        self.apellido = apellido
        self.canal = canal
        self.destinatario = destinatario

    def _obtener_apellido(self):
        try:
            apellido = Apellido.objects.get(apellido=self.apellido)
            return apellido
        except Apellido.DoesNotExist:
            raise ValueError("Apellido no encontrado")
        
    def _obtener_distribuciones(self):
        distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=self._obtener_apellido())
        return distribuciones

    def _enviar_por_canal(self, distribuciones: Dict):
        try:
            apellido_obj = self._obtener_apellido()
            generador_mensaje = GeneradorMensaje()
            mensaje = generador_mensaje.generar(apellido_obj, distribuciones)

            if self.canal == "email":
                tarea_compartir_email.delay(
                    asunto=mensaje.asunto,
                    cuerpo=mensaje.cuerpo,
                    destinatario=self.destinatario,
                    cuerpo_html=mensaje.cuerpo_html,
                )
                return ResultadoEnvio(
                    estado=EstadoEnvio.ACEPTADO,
                    canal=self.canal,
                    mensaje="La solicitud de envío ha sido aceptada y se está procesando en segundo plano."
                )
            return ResultadoEnvio(
                estado=EstadoEnvio.FALLIDO,
                canal=self.canal,
                mensaje="Canal no soportado."
            )
        except Exception as e:
            return ResultadoEnvio(
                estado=EstadoEnvio.FALLIDO,
                canal=self.canal,
                mensaje=f"Error al compartir: {str(e)}"
            )

    def ejecutar(self):
        distribuciones = self._obtener_distribuciones()
        return self._enviar_por_canal(distribuciones)
            
        