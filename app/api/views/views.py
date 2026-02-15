from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.api.serializers.apellido_serializer import ApellidoEntradaSerializer, DistribucionApellidoRespuestaSerializer
from app.api.serializers.compartir_serializer import SolicitudCompartirSerializer, RespuestaCompartirSerializer
from app.domain.services.obtener_apellido import obtener_informacion_apellido, consultar_estado_apellido
from app.domain.services.unificar_apellidos import UnificarApellidosService
from app.validators.apellido import validar_apellido
from app.shared.compartir_service import ServicioCompartir
from app.shared.email_sender import EstadoEnvio


class ApellidoView(APIView):
    def post(self, request):
        serializer = ApellidoEntradaSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lista_apellidos = serializer.context["lista_apellidos"]
            lista_originales = serializer.context["lista_originales"]
            
            resultados = []
            for norm, orig in zip(lista_apellidos, lista_originales):
                info = obtener_informacion_apellido(norm, orig)
                resultados.append(info)
            
            unificador = UnificarApellidosService()
            resultado_unificado = unificador.ejecutar(resultados)
            
            response = DistribucionApellidoRespuestaSerializer(resultado_unificado)
            
            return Response(
                response.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"mensaje": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, apellido):
        resultado_validacion = validar_apellido(apellido)

        if not resultado_validacion["es_valido"]:
            return Response(
                {"error": resultado_validacion["error"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lista_apellidos = resultado_validacion["lista_apellidos"]
            lista_originales = resultado_validacion["lista_originales"]
            
            resultados = []
            for norm, orig in zip(lista_apellidos, lista_originales):
                info = obtener_informacion_apellido(norm, orig)
                resultados.append(info)
            
            unificador = UnificarApellidosService()
            resultado_unificado = unificador.ejecutar(resultados)

            estado = resultado_unificado.get('estado')
            if estado == "encontrado":
                http_status = status.HTTP_200_OK
            elif estado == "procesando":
                http_status = status.HTTP_202_ACCEPTED
            elif estado == "no_encontrado":
                http_status = status.HTTP_404_NOT_FOUND
            else:
                http_status = status.HTTP_400_BAD_REQUEST

            response = DistribucionApellidoRespuestaSerializer(resultado_unificado)
            
            return Response(
                response.data,
                status=http_status
            )
        except Exception as e:
            return Response(
                {"mensaje": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CompartirView(APIView):
    def post(self, request):
        serializer = SolicitudCompartirSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            apellido_normalizado = serializer.context["apellido_normalizado"]
            canal = serializer.validated_data['canal']
            destinatario = serializer.validated_data['destinatario']

            servicio = ServicioCompartir(apellido_normalizado, canal, destinatario)
            resultado = servicio.ejecutar()
            
            http_status = status.HTTP_202_ACCEPTED if resultado.estado == EstadoEnvio.ACEPTADO else status.HTTP_400_BAD_REQUEST
            response = RespuestaCompartirSerializer(resultado)

            return Response(
                {"mensaje": response.data},
                status=http_status
            )
        except Exception as e:
            return Response(
                {"mensaje": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )