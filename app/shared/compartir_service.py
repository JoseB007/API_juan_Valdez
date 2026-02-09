from typing import Dict

from .constructor_mensaje import ConstructorMensajeCompartido
from .email_sender import EmailSender, ResultadoCompartido, EstadoCompartido
from ..domain.models.models import DistribucionApellidoDepartamento, Apellido


class Compartir:
    def __init__(self, apellido: str, canal: str, destinatario: str):
        self.apellido = apellido
        self.canal = canal
        self.destinatario = destinatario

    def obtener_obj_apellido(self):
        try:
            apellido = Apellido.objects.get(apellido=self.apellido)
            return apellido
        except Apellido.DoesNotExist:
            raise ValueError("Apellido no encontrado")
        
    def obtener_distribuciones(self):
        distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=self.obtener_obj_apellido())
        return distribuciones

    def compartir(self, distribuciones: Dict):
        try:
            apellido_obj = self.obtener_obj_apellido()
            constructor_mensaje = ConstructorMensajeCompartido()
            mensaje = constructor_mensaje.construir(apellido_obj, distribuciones)

            if self.canal == "email":
                email_sender = EmailSender()
                return email_sender.send(
                    asunto=mensaje.asunto, 
                    cuerpo=mensaje.cuerpo, 
                    destinatario=self.destinatario
                )
            # elif self.canal == "whatsapp":
            #     whatsapp_sender = WhatsAppSender()
            #     whatsapp_sender.send(mensaje.cuerpo)
            return ResultadoCompartido(
                estado=EstadoCompartido.FALLIDO,
                canal="email",
                mensaje="Canal no soportado."
            )
        except Exception as e:
            print(f"Error al compartir: {str(e)}")

    def ejecutar(self):
        distribuciones = self.obtener_distribuciones()
        self.compartir(distribuciones)
            
        