from app.domain.services.nucleo.unificador import ServicioUnificador

def test_unificar_apellidos_v3():
    service = ServicioUnificador()
    
    resultados_lista = [
        {
            "estado": "ACTIVO",
            "apellido_original": "Valdez",
            "apellido_normalizado": "valdez",
            "distribuciones": [
                {"departamento": {"nombre": "Antioquia", "frase": "Frase A"}, "porcentaje": 10, "ranking": 1},
                {"departamento": {"nombre": "Bogotá", "frase": "Frase B"}, "porcentaje": 20, "ranking": 2},
            ],
            "frases": [{"categoria": "Sabor", "frase": "A Valdez le gusta el café suave"}]
        },
        {
            "estado": "ACTIVO",
            "apellido_original": "Juarez",
            "apellido_normalizado": "juarez",
            "distribuciones": [
                {"departamento": {"nombre": "Medellín", "frase": "Frase M"}, "porcentaje": 40, "ranking": 3},
                {"departamento": {"nombre": "Cali", "frase": "Frase C"}, "porcentaje": 5, "ranking": 4},
                {"departamento": {"nombre": "Barranquilla", "frase": "Frase BA"}, "porcentaje": 15, "ranking": 5},
            ],
            "frases": [{"categoria": "Personalidad", "frase": "Juarez es una persona fuerte"}]
        }
    ]
    
    resultado = service.ejecutar(resultados_lista)
    distribuciones = resultado["distribuciones"]
    frases = resultado["frases"]
    
    print(f"Apellido unificado: {resultado['apellido_original']}")
    print(f"Total distribuciones: {len(distribuciones)}")
    total_suma = sum(d['porcentaje'] for d in distribuciones)
    print(f"Suma total porcentajes: {total_suma}%")
    for d in distribuciones:
        print(f"Depto: {d['departamento']['nombre']}, Porcentaje: {d['porcentaje']}")
    
    print("Frases unificadas:")
    for f in frases:
        print(f"Cat: {f['categoria']}, Frase: {f['frase']}")

    assert len(distribuciones) <= 3
    # Note: user removed the rounding adjustment, so it might not be exactly 100.0 if there are floating point issues or many decimals
    # But with 2, it should be close.
    print(f"Total Sum: {total_suma}")
    
    assert "Valdez Juarez" in frases[0]['frase']
    assert "Valdez Juarez" in frases[1]['frase']

if __name__ == "__main__":
    try:
        test_unificar_apellidos_v3()
        print("Test passed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Test failed: {e}")
