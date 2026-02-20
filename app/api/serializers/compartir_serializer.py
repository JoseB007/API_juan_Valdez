from rest_framework import serializers
from app.validators.apellido import validar_apellido


class SolicitudCompartirSerializer(serializers.Serializer):
    apellido = serializers.CharField()
    canal = serializers.ChoiceField(choices=["email", "whatsapp"])
    destinatario = serializers.CharField()

    def validate(self, data):
        canal = data.get("canal")
        destinatario = data.get("destinatario")

        if canal == "email":
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(destinatario)
            except ValidationError:
                raise serializers.ValidationError({"destinatario": "Debe ser un correo electrónico válido."})
        
        elif canal == "whatsapp":
            import re
            # Formato E.164: + seguido de 1-15 dígitos
            whatsapp_regex = r"^\+[1-9]\d{1,14}$"
            if not re.match(whatsapp_regex, destinatario):
                raise serializers.ValidationError({"destinatario": "El número de WhatsApp debe tener un formato internacional válido (ej: +573012345678)."})
        
        return data

    def validate_apellido(self, value):
        resultado = validar_apellido(value)

        if not resultado["es_valido"]:
            raise serializers.ValidationError(resultado["error"])
        
        self.context["apellido_normalizado"] = resultado["normalizado"]
        self.context["lista_apellidos"] = resultado["lista_apellidos"]
        self.context["lista_originales"] = resultado["lista_originales"]
        return value
    

class RespuestaCompartirSerializer(serializers.Serializer):
    estado = serializers.CharField()
    canal = serializers.CharField()
    mensaje = serializers.CharField()