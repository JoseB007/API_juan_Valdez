from typing import Dict
from django.template.loader import render_to_string

from .entidades import Mensaje


class GeneradorMensaje:
    """
    Generador de mensaje compartido que crea un mensaje con el asunto y el cuerpo.
    """
    def generar(self, info_apellidos: Dict) -> Mensaje:
        apellido = info_apellidos.get("apellido_original")
        distribuciones = info_apellidos.get("distribuciones")
        frases = info_apellidos.get("frases")

        asunto = f"Resultado de búsqueda para el apellido {apellido}"
        cuerpo = self._generar_cuerpo(distribuciones, frases, apellido)
        cuerpo_html = self._generar_html(distribuciones, frases, apellido, asunto)
        
        return Mensaje(
            asunto=asunto,
            cuerpo=cuerpo,
            cuerpo_html=cuerpo_html
        )

    def _generar_cuerpo(self, distribuciones: Dict, frases: Dict, apellido) -> str:
        lineas = []
        
        lineas.append(f"Resultados de búsqueda para el apellido: {apellido}")
        lineas.append("-" * 40)
        lineas.append("")

        if distribuciones:
            lineas.append("Distribuciones encontradas:")
            for distribucion in distribuciones:
                if hasattr(distribucion, 'departamento'):
                    # Si es un objeto (modelo Django)
                    nombre_dept = distribucion.departamento.nombre
                    porcentaje = distribucion.porcentaje
                    ranking = distribucion.ranking
                else:
                    # Si es un diccionario (resultado de UnificarApellidosService)
                    nombre_dept = distribucion['departamento']['nombre']
                    porcentaje = distribucion['porcentaje']
                    ranking = distribucion['ranking']

                lineas.append(f"- Departamento: {nombre_dept}")
                lineas.append(f"  Apellido: {apellido}")
                lineas.append(f"  Porcentaje: {porcentaje}%")
                lineas.append(f"  Ranking: #{ranking}")
                lineas.append("")
        else:
            lineas.append("No se encontraron distribuciones.")
            lineas.append("")

        if frases:
            lineas.append("-" * 40)
            lineas.append("Curiosidades y Datos:")
            for frase in frases:
                if hasattr(frase, 'categoria'):
                    # Si es un objeto
                    categoria = frase.categoria
                    texto = frase.frase
                else:
                    # Si es un diccionario
                    categoria = frase['categoria']
                    texto = frase['frase']

                lineas.append(f"\n* {categoria}:")
                lineas.append(f"  {texto}")

        return "\n".join(lineas)

    def _generar_html(self, distribuciones: Dict, frases: Dict, apellido, asunto: str) -> str:
        context = {
            'asunto': asunto,
            'distribuciones': distribuciones,
            'apellido': apellido,
            'frases': frases
        }
        return render_to_string('shared/mensaje.html', context)
