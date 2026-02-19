from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.api.serializers.apellido_serializer import ApellidoEntradaSerializer, DistribucionApellidoRespuestaSerializer
from app.domain.services.nucleo.procesador import ServicioProcesarMultiplesApellidos, consultar_estado_apellido
from app.domain.services.nucleo.unificador import ServicioUnificador
from app.validators.apellido import validar_apellido


class ApellidoView(APIView):
    def post(self, request):
        serializer = ApellidoEntradaSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lista_apellidos = serializer.context["lista_apellidos"]
        lista_originales = serializer.context["lista_originales"]
        
        procesador = ServicioProcesarMultiplesApellidos()
        resultado_unificado = procesador.ejecutar(lista_apellidos, lista_originales)
        
        estado = resultado_unificado.get('estado')
        if estado not in ["encontrado", "procesando"]:
            return Response(
                {"mensaje": resultado_unificado.get("mensaje", "No se encontró información")},
                status=status.HTTP_404_NOT_FOUND if estado == "no_encontrado" else status.HTTP_400_BAD_REQUEST
            )

        response = DistribucionApellidoRespuestaSerializer(resultado_unificado)
        
        return Response(
            response.data,
            status=status.HTTP_200_OK if estado == "encontrado" else status.HTTP_202_ACCEPTED
        )

    def get(self, request, apellido):
        resultado_validacion = validar_apellido(apellido)

        if not resultado_validacion["es_valido"]:
            return Response(
                {"error": resultado_validacion["error"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        lista_apellidos = resultado_validacion["lista_apellidos"]
        lista_originales = resultado_validacion["lista_originales"]
        
        resultados = []
        for norm, orig in zip(lista_apellidos, lista_originales):
            info = consultar_estado_apellido(norm, orig)
            resultados.append(info)
        
        unificador = ServicioUnificador()
        resultado_unificado = unificador.ejecutar(resultados)

        estado = resultado_unificado.get('estado')
        if estado not in ["encontrado", "procesando"]:
            return Response(
                {"mensaje": resultado_unificado.get("mensaje", "No se encontró información para uno o más apellidos")},
                status=status.HTTP_404_NOT_FOUND if estado == "no_encontrado" else status.HTTP_400_BAD_REQUEST
            )

        response = DistribucionApellidoRespuestaSerializer(resultado_unificado)
        
        return Response(
            response.data,
            status=status.HTTP_200_OK
        )

