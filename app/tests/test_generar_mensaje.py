from django.test import TestCase
from app.shared.generar_mensaje import GeneradorMensaje
from app.domain.models.apellido_models import DistribucionApellidoDepartamento, Apellido, Frases
from typing import Dict
from unittest.mock import MagicMock

class GeneradorMensajeTestCase(TestCase):
    def setUp(self):
        # Create dummy data for testing
        self.apellido = "Gomez"
        # We need to mock the database models or use dummy objects if direct instantiation is possible
        # Since we are testing logic that uses models, we might need valid model instances or mocks.
        # Let's use simple dataclasses or mocks to simulate model instances if possible,
        # but GeneradorMensaje accesses .departamento, .apellido, .porcentaje, .ranking directly.
        
        # Mocking distributions
        self.distribucion1 = MagicMock()
        self.distribucion1.departamento = "Antioquia"
        self.distribucion1.apellido = "Gomez"
        self.distribucion1.porcentaje = 15.5
        self.distribucion1.ranking = 1

        self.distribuciones = [self.distribucion1]

        # Mocking Frases query
        # Since Frases.objects.filter is called inside the method, we need to mock Frases.objects.filter
        # However, patching inside a test method is cleaner.
        
    def test_generar_mensaje_html(self):
        # Arrange
        generador = GeneradorMensaje()
        
        # Act
        mensaje = generador.generar(self.apellido, self.distribuciones)
        
        # Assert
        self.assertIsNotNone(mensaje.cuerpo_html)
        self.assertIn("<!DOCTYPE html>", mensaje.cuerpo_html)
        self.assertIn("<h1>Resultado de búsqueda para el apellido Gomez</h1>", mensaje.cuerpo_html)
        self.assertIn("Antioquia", mensaje.cuerpo_html)
        self.assertIn("15.5%", mensaje.cuerpo_html)
        self.assertIn("#1", mensaje.cuerpo_html)
        
    def test_generar_mensaje_texto_plano(self):
        # Arrange
        generador = GeneradorMensaje()
        
        # Act
        mensaje = generador.generar(self.apellido, self.distribuciones)
        
        # Assert
        self.assertIsNotNone(mensaje.cuerpo)
        self.assertIn("Se han encontrado las siguientes distribuciones", mensaje.cuerpo)
        self.assertIn("Antioquia", mensaje.cuerpo)
        self.assertIn("15.5%", mensaje.cuerpo)
