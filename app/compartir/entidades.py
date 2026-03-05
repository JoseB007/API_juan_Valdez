from enum import Enum
from dataclasses import dataclass

class EstadoEnvio(Enum):
    ACEPTADO = "ACEPTADO"
    FALLIDO = "FALLIDO"

@dataclass
class ResultadoEnvio:
    estado: EstadoEnvio
    canal: str
    mensaje: str

@dataclass
class Mensaje:
    asunto: str
    cuerpo: str
    cuerpo_html: str = None
