from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.api.serializers.compartir_serializer import SolicitudCompartirSerializer, RespuestaCompartirSerializer
from app.shared.compartir_service import ServicioCompartir
from app.shared.email_sender import EstadoEnvio


class CompartirView(APIView):
    def post(self, request):
        serializer = SolicitudCompartirSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lista_apellidos = serializer.context["lista_apellidos"]
        lista_originales = serializer.context["lista_originales"]

        canal = serializer.validated_data['canal']
        destinatario = serializer.validated_data['destinatario']

        servicio = ServicioCompartir(lista_originales, lista_apellidos, canal, destinatario)
        resultado = servicio.ejecutar()
        
        http_status = status.HTTP_202_ACCEPTED if resultado.estado == EstadoEnvio.ACEPTADO else status.HTTP_400_BAD_REQUEST
        response = RespuestaCompartirSerializer(resultado)

        return Response(
            {"mensaje": response.data},
            status=http_status
        )