import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from app.domain.models.apellido_models import Apellido, Departamento, DistribucionApellidoDepartamento, Frases

@pytest.mark.django_db
class TestApellidoPolling:
    def setup_method(self):
        self.client = APIClient()

    def test_polling_no_encontrado(self):
        url = reverse('apellido_poll', kwargs={'apellido': 'Inexistente'})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['estado'] == 'no_encontrado'

    def test_polling_procesando(self):
        Apellido.objects.create(apellido='ROSERO', estado=Apellido.PENDIENTE)
        
        url = reverse('apellido_poll', kwargs={'apellido': 'Rosero'})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data['estado'] == 'procesando'
        assert response.data['apellido_normalizado'] == 'ROSERO'

    def test_polling_listo(self):
        apellido_obj = Apellido.objects.create(
            apellido='ROSERO', 
            estado=Apellido.LISTO,
            fuente='Prueba'
        )
        # Add some data
        dept = Departamento.objects.create(nombre='Nariño', frase='Frase test')
        DistribucionApellidoDepartamento.objects.create(
            apellido=apellido_obj,
            departamento=dept,
            porcentaje=10.5,
            ranking=1
        )
        Frases.objects.create(
            apellido=apellido_obj,
            categoria='PERSONALIDAD',
            frase='Es una persona amable'
        )
        
        url = reverse('apellido_poll', kwargs={'apellido': 'Rosero'})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['estado'] == 'encontrado'
        assert len(response.data['distribuciones']) == 1
        assert len(response.data['frases']) == 1
        assert response.data['distribuciones'][0]['departamento']['nombre'] == 'Nariño'

    def test_post_inicia_procesando(self):
        # This tests the POST starts the process and returns the status
        # Note: Depending on how the service is mocked, we might see 'procesando' or full data.
        # Here we just want to ensure the endpoint exists and responds.
        url = reverse('apellido')
        data = {'apellido': 'Rosero'}
        response = self.client.post(url, data)
        
        # If it's a new surname, it might return 'procesando' or try to call external APIs.
        # For simplicity in this test, we just check for 200/202.
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
