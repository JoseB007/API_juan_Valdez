from typing import Dict

from .generar_mensaje import GeneradorMensaje
from .email_sender import EnviadorCorreo, ResultadoEnvio, EstadoEnvio
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
                enviador = EnviadorCorreo()
                return enviador.enviar(
                    asunto=mensaje.asunto, 
                    cuerpo=mensaje.cuerpo, 
                    destinatario=self.destinatario,
                    cuerpo_html=mensaje.cuerpo_html
                )
            # elif self.canal == "whatsapp":
            #     whatsapp_sender = WhatsAppSender()
            #     whatsapp_sender.send(mensaje.cuerpo)
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
            
        