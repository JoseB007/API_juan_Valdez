from rest_framework import serializers
from app.validators.apellido import validar_apellido


class ApellidoSerializer(serializers.Serializer):
    apellido = serializers.CharField(max_length=30, required=True)

    def validate_apellido(self, value):
        resultado = validar_apellido(value)

        if not resultado["es_valido"]:
            raise serializers.ValidationError(resultado["error"])
        
        self.context["apellido_normalizado"] = resultado["normalizado"]
        return value


    