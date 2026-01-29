from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.api.serializers.apellido_serializer import ApellidoSerializer
from app.domain.services.obtener_apellido import obtener_informacion_apellido


class ApellidoView(APIView):
    def post(self, request):
        serializers = ApellidoSerializer(data=request.data)

        if not serializers.is_valid():
            return Response(
                serializers.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        apellido_normalizado = serializers.context["apellido_normalizado"]
        apellido_original = serializers.validated_data['apellido']
        info_apellido = obtener_informacion_apellido(apellido_normalizado, apellido_original)

        return Response(
            info_apellido,
            status=status.HTTP_200_OK
        )
        