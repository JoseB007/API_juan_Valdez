from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from typing import Dict
from app.domain.models.apellido_models import Apellido, DistribucionApellidoDepartamento, Frases


class ApellidoRepository:
    """
    Encapsula todas las operaciones de persistencia y consultas complejas 
    relacionadas con el modelo Apellido para evitar lógica de BD en el orquestador.
    """
    
    @staticmethod
    def obtener_o_crear_inicial(apellido_normalizado: str) -> tuple[Apellido, bool]:
        with transaction.atomic():
            apellido_obj, created = Apellido.objects.get_or_create(
                apellido=apellido_normalizado,
                defaults={'estado': Apellido.PENDIENTE, 'fuente': 'Buscando...'}
            )
            return Apellido.objects.select_for_update().get(pk=apellido_obj.pk), created

    @staticmethod
    def obtener_datos_completos(apellido_obj: Apellido) -> Dict:
        """Carga distribuciones y frases desde la base de datos."""
        distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
        frases = Frases.objects.filter(apellido=apellido_obj)
        
        return {
            "distribuciones": list(distribuciones),
            "frases": list(frases),
            "tiene_distribuciones": len(distribuciones) > 0,
            "tiene_frases": len(frases) > 0
        }

    @staticmethod
    def reiniciar_estado_pendiente(apellido_obj: Apellido):
        Apellido.objects.filter(pk=apellido_obj.pk).update(
            estado=Apellido.PENDIENTE,
            created_at=timezone.now()
        )

    @staticmethod
    def marcar_como_listo(apellido_obj: Apellido):
        if apellido_obj.estado != Apellido.LISTO:
            apellido_obj.estado = Apellido.LISTO
            apellido_obj.save()

    @staticmethod
    def marcar_como_fallido(apellido_normalizado: str):
        Apellido.objects.filter(apellido=apellido_normalizado).update(estado=Apellido.FALLIDO)


class ApellidoPolicy:
    """
    Encapsula las reglas de negocio para determinar el flujo a seguir basándose 
    en el estado y los datos actuales de un apellido.
    """
    
    @staticmethod
    def esta_procesando(apellido_obj: Apellido) -> bool:
        esta_caducado = (timezone.now() - apellido_obj.created_at) > timedelta(minutes=1)
        return apellido_obj.estado == Apellido.PENDIENTE and not esta_caducado

    @staticmethod
    def requiere_procesamiento_externo(datos_db: Dict) -> bool:
        """Determina si necesitamos llamar a Onograph/IA."""
        # Si no hay distribuciones, definitivamente necesitamos procesamiento externo
        return not datos_db["tiene_distribuciones"]

    @staticmethod
    def esta_completo(datos_db: Dict) -> bool:
        """Determina si el apellido ya tiene toda la información necesaria."""
        return datos_db["tiene_distribuciones"] and datos_db["tiene_frases"]
