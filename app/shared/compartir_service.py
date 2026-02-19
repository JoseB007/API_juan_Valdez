from typing import Dict

from .generar_mensaje import GeneradorMensaje
from .email_sender import ResultadoEnvio, EstadoEnvio
from .tasks import tarea_compartir_email
from app.domain.models.apellido_models import DistribucionApellidoDepartamento, Apellido, Frases
from app.domain.services.nucleo.unificador import ServicioUnificador
from app.api.exceptions.apellido_exceptions import BrokerConnectionError


class ServicioCompartir:
    def __init__(self, apellidos_originales: list, apellidos_normalizados: list, canal: str, destinatario: str):
        self.apellidos_originales = apellidos_originales
        self.apellidos_normalizados = apellidos_normalizados
        self.canal = canal
        self.destinatario = destinatario

    def _obtener_info_apellidos(self):
        try:
            resultados = []
            for orig, norm in zip(self.apellidos_originales, self.apellidos_normalizados):
                apellido_obj = Apellido.objects.get(apellido=norm)
                distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
                frases = Frases.objects.filter(apellido=apellido_obj)
                
                resultados.append({
                    "estado": "encontrado",
                    "fuente": apellido_obj.fuente,
                    "apellido_original": orig,
                    "apellido_normalizado": apellido_obj.apellido,
                    "distribuciones": list(distribuciones),
                    "frases": list(frases)
                })

            unificador = ServicioUnificador()
            resultados_unificados = unificador.ejecutar(resultados)
            
            return resultados_unificados
        except Apellido.DoesNotExist:
            raise ValueError("Apellido no encontrado")

    def _enviar_por_canal(self):
        try:
            info_apellidos = self._obtener_info_apellidos()
            generador_mensaje = GeneradorMensaje()
            mensaje = generador_mensaje.generar(info_apellidos)

            if self.canal == "email":
                try:
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
                except Exception as e:
                    # Si falla al encolar, es un error de infraestructura (Broker Redis)
                    raise BrokerConnectionError(f"No se pudo programar el envío. El servicio de colas puede estar no disponible. Detalles: {str(e)}")
            
            return ResultadoEnvio(
                estado=EstadoEnvio.FALLIDO,
                canal=self.canal,
                mensaje="Canal no soportado."
            )
        except BrokerConnectionError as e:
            raise e
        except Exception as e:
            return ResultadoEnvio(
                estado=EstadoEnvio.FALLIDO,
                canal=self.canal,
                mensaje=f"Error al compartir: {str(e)}"
            )

    def ejecutar(self):
        return self._enviar_por_canal()
            
        