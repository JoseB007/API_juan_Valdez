from typing import Dict
from dataclasses import dataclass

from ..domain.models.models import Frases

@dataclass
class MensajeCompartido:
    asunto: str
    cuerpo: str


class ConstructorMensajeCompartido:
    """
    Constructor de mensaje compartido que crea un mensaje con el asunto y el cuerpo.
    """
    def _construir(self, distribuciones: Dict, apellido) -> MensajeCompartido:
        return MensajeCompartido(
            asunto="Resultado de búsqueda de distribuciones",
            cuerpo=self._construir_cuerpo(distribuciones, apellido)
        )

    def _construir_cuerpo(self, distribuciones: Dict, apellido) -> str:
        lineas = []

        if distribuciones:
            for distribucion in distribuciones:
                lineas.append(f"Se han encontrado las siguientes distribuciones en el departamento de {distribucion.departamento} para tu apellido {distribucion.apellido}")
                lineas.append(f"Porcentaje: {distribucion.porcentaje}%")
                lineas.append(f"Ranking: {distribucion.ranking}")
                lineas.append("")

        frases = Frases.objects.filter(apellido=apellido)
        if frases:
            for frase in frases:
                lineas.append(f"\n{frase.categoria}: {frase.frase}")

        return "\n".join(lineas)

                
