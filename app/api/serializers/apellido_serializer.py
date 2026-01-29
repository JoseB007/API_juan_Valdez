from rest_framework import serializers
from app.validators.apellido import validar_apellido
from app.domain.models.models import (
    DistribucionApellidoDepartamento,
    Frases
)

class ApellidoSerializer(serializers.Serializer):
    apellido = serializers.CharField(max_length=30, required=True)

    def validate_apellido(self, value):
        resultado = validar_apellido(value)

        if not resultado["es_valido"]:
            raise serializers.ValidationError(resultado["error"])
        
        self.context["apellido_normalizado"] = resultado["normalizado"]
        return value


class DistribucionSerializer(serializers.Serializer):
    departamento = serializers.SerializerMethodField()
    porcentaje = serializers.FloatField()
    ranking = serializers.IntegerField()
    origen = serializers.CharField(required=False, default="REAL")

    def get_departamento(self, obj):
        if isinstance(obj, dict):
            return obj.get("departamento")
        return obj.departamento.nombre


class FraseSerializer(serializers.Serializer):
    categoria = serializers.CharField()
    frase = serializers.CharField()
    origen = serializers.CharField()


class ApellidoRespuestaSerializer(serializers.Serializer):
    estado = serializers.CharField()
    origen = serializers.CharField()
    apellido_original = serializers.CharField()
    apellido_normalizado = serializers.CharField()
    departamentos = DistribucionSerializer(many=True)
    frases = FraseSerializer(many=True)