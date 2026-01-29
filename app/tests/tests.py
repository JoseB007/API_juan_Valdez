from django.test import TestCase

import pytest
from app.validators.apellido import validar_apellido


@pytest.mark.parametrize("apellido, expected", [
    ("Gomez", "GOMEZ"),
    ("Gómez", "GOMEZ"),
    ("Muñoz", "MUNOZ"),
    ("Ávila", "AVILA"),
    ("Lopez", "LOPEZ"),
    ("Perez", "PEREZ"),
    ("Rodriguez", "RODRIGUEZ"),
    ("Sanchez", "SANCHEZ"),
    ("Torres", "TORRES"),
    ("Vasquez", "VASQUEZ"),
])
def test_validar_apellido(apellido, expected):
    resultado = validar_apellido(apellido)
    
    assert resultado["es_valido"] is True
    assert resultado["error"] is None
    assert resultado["normalizado"] == expected


@pytest.mark.parametrize("apellido", [
    None,
    "",
])
def test_apellido_vacio(apellido):
    resultado = validar_apellido(apellido)
    
    assert resultado["es_valido"] is False
    assert resultado["error"] == "El apellido es obligatorio"
    assert resultado["normalizado"] is None


@pytest.mark.parametrize("apellido", [
    " Gomez",
    "Gomez ",
    " Gomez ",
])
def test_apellido_con_espacios_inicio_fin(apellido):
    resultado = validar_apellido(apellido)
    
    assert resultado["es_valido"] is False
    assert resultado["error"] == "El apellido no debe contener espacios al inicio o al final"
    assert resultado["normalizado"] is None


@pytest.mark.parametrize("apellido", [
    "G",
    "Gomez Perez",
    "Gomez1",
    "Gómez-Álvarez",
    "Gomez!",
    "Go mez",
])
def test_apellido_formato_invalido(apellido):
    resultado = validar_apellido(apellido)
    
    assert resultado["es_valido"] is False
    assert resultado["error"] == "El apellido debe tener entre 2 y 30 letras y no contener espacios ni caracteres especiales"
    assert resultado["normalizado"] is None