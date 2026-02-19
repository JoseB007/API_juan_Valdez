import pytest
from app.domain.services.nucleo.unificador import ServicioUnificador

def test_unificar_estado_mixto_uno_pendiente():
    service = ServicioUnificador()
    
    resultados = [
        {
            "estado": "encontrado",
            "apellido_original": "Perez",
            "apellido_normalizado": "PEREZ",
            "distribuciones": [{"departamento": {"nombre": "Bogota", "frase": "X"}, "porcentaje": 100, "ranking": 1}],
            "frases": []
        },
        {
            "estado": "procesando",
            "apellido_original": "Gomez",
            "apellido_normalizado": "GOMEZ",
            "distribuciones": [],
            "frases": []
        }
    ]
    
    resultado_final = service.ejecutar(resultados)
    
    assert resultado_final["estado"] == "procesando"
    assert resultado_final["distribuciones"] == []
    assert "Perez Gomez" in resultado_final["apellido_original"]

def test_unificar_ambos_encontrados():
    service = ServicioUnificador()
    
    resultados = [
        {
            "estado": "encontrado",
            "apellido_original": "Perez",
            "apellido_normalizado": "PEREZ",
            "distribuciones": [{"departamento": {"nombre": "Bogota", "frase": "X"}, "porcentaje": 100, "ranking": 1}],
            "frases": []
        },
        {
            "estado": "encontrado",
            "apellido_original": "Gomez",
            "apellido_normalizado": "GOMEZ",
            "distribuciones": [{"departamento": {"nombre": "Bogota", "frase": "X"}, "porcentaje": 100, "ranking": 1}],
            "frases": []
        }
    ]
    
    resultado_final = service.ejecutar(resultados)
    
    assert resultado_final["estado"] == "encontrado"
    assert len(resultado_final["distribuciones"]) > 0

def test_unificar_estado_error_y_encontrado():
    service = UnificarApellidosService()
    
    resultados = [
        {
            "estado": "encontrado",
            "apellido_original": "Perez",
            "apellido_normalizado": "PEREZ",
            "distribuciones": [{"departamento": {"nombre": "Bogota", "frase": "X"}, "porcentaje": 100, "ranking": 1}],
            "frases": []
        },
        {
            "estado": "error",
            "apellido_original": "Gomez",
            "apellido_normalizado": "GOMEZ",
            "distribuciones": [],
            "frases": []
        }
    ]
    
    resultado_final = service.ejecutar(resultados)
    
    # Según nuestra lógica: "encontrado" tiene prioridad sobre "error" si no hay "procesando"
    assert resultado_final["estado"] == "encontrado"
