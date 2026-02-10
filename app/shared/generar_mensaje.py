from typing import Dict
from django.template.loader import render_to_string
from dataclasses import dataclass

from ..domain.models.models import Frases


@dataclass
class Mensaje:
    asunto: str
    cuerpo: str
    cuerpo_html: str = None


class GeneradorMensaje:
    """
    Generador de mensaje compartido que crea un mensaje con el asunto y el cuerpo.
    """
    def generar(self, apellido, distribuciones: Dict) -> Mensaje:
        asunto = f"Resultado de búsqueda para el apellido {apellido}"
        cuerpo = self.generar_cuerpo(distribuciones, apellido)
        cuerpo_html = self._generar_html(distribuciones, apellido, asunto)
        
        return Mensaje(
            asunto=asunto,
            cuerpo=cuerpo,
            cuerpo_html=cuerpo_html
        )

    def generar_cuerpo(self, distribuciones: Dict, apellido) -> str:
        lineas = []
        
        lineas.append(f"Resultados de búsqueda para el apellido: {apellido}")
        lineas.append("-" * 40)
        lineas.append("")

        if distribuciones:
            lineas.append("Distribuciones encontradas:")
            for distribucion in distribuciones:
                lineas.append(f"- Departamento: {distribucion.departamento}")
                lineas.append(f"  Apellido: {distribucion.apellido}")
                lineas.append(f"  Porcentaje: {distribucion.porcentaje}%")
                lineas.append(f"  Ranking: #{distribucion.ranking}")
                lineas.append("")
        else:
            lineas.append("No se encontraron distribuciones.")
            lineas.append("")

        frases = Frases.objects.filter(apellido=apellido)
        if frases:
            lineas.append("-" * 40)
            lineas.append("Curiosidades y Datos:")
            for frase in frases:
                lineas.append(f"\n* {frase.categoria}:")
                lineas.append(f"  {frase.frase}")

        return "\n".join(lineas)

    def _generar_html(self, distribuciones: Dict, apellido, asunto: str) -> str:
        frases = Frases.objects.filter(apellido=apellido)
        context = {
            'asunto': asunto,
            'distribuciones': distribuciones,
            'apellido': apellido,
            'frases': frases
        }
        return render_to_string('shared/mensaje.html', context)
