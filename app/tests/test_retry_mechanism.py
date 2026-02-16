import pytest
from django.utils import timezone
from datetime import timedelta
from app.domain.models.models import Apellido
from app.domain.services.obtener_apellido import obtener_informacion_apellido
from unittest.mock import patch

@pytest.mark.django_db
class TestRetryMechanism:
    
    @patch('app.domain.services.obtener_apellido.ObtenerApellidoAPIOnograph')
    def test_reprocesar_apellido_stale(self, mock_api):
        # 1. Crear un apellido PENDIENTE antiguo (hace 10 minutos)
        hace_10_mins = timezone.now() - timedelta(minutes=10)
        apellido_obj = Apellido.objects.create(
            apellido='STALE_TEST',
            estado=Apellido.PENDIENTE,
            fuente='Buscando...'
        )
        # Forzar la fecha de creación (auto_now_add=True requiere update manual o mock)
        Apellido.objects.filter(id=apellido_obj.id).update(created_at=hace_10_mins)
        
        # Mock de la respuesta del API para que no falle realmente
        mock_api.return_value.ejecutar.return_value = {"estado": "encontrado"}

        # 2. Llamar al servicio
        resultado = obtener_informacion_apellido('STALE_TEST', 'Stale_Test')

        # 3. Verificar que se intentó ejecutar el servicio de nuevo
        assert mock_api.called
        assert resultado == {"estado": "encontrado"}

    @patch('app.domain.services.obtener_apellido.ObtenerApellidoAPIOnograph')
    def test_no_reprocesar_apellido_reciente(self, mock_api):
        # 1. Crear un apellido PENDIENTE reciente (hace 1 minuto)
        hace_1_min = timezone.now() - timedelta(minutes=1)
        apellido_obj = Apellido.objects.create(
            apellido='RECENT_TEST',
            estado=Apellido.PENDIENTE,
            fuente='Buscando...'
        )
        Apellido.objects.filter(id=apellido_obj.id).update(created_at=hace_1_min)

        # 2. Llamar al servicio
        resultado = obtener_informacion_apellido('RECENT_TEST', 'Recent_Test')

        # 3. Verificar que NO se ejecutó el servicio y devolvió 'procesando'
        assert not mock_api.called
        assert resultado['estado'] == 'procesando'

    @patch('app.domain.services.obtener_apellido.ObtenerApellidoAPIOnograph')
    def test_reprocesar_apellido_fallido(self, mock_api):
        # 1. Crear un apellido FALLIDO
        Apellido.objects.create(
            apellido='FAILED_TEST',
            estado=Apellido.FALLIDO,
            fuente='Error previo'
        )
        
        mock_api.return_value.ejecutar.return_value = {"estado": "encontrado"}

        # 2. Llamar al servicio
        resultado = obtener_informacion_apellido('FAILED_TEST', 'Failed_Test')

        # 3. Verificar que se intentó de nuevo
        assert mock_api.called
        assert resultado == {"estado": "encontrado"}
