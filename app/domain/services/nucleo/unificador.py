from typing import List, Dict

from app.domain.services.nucleo.soporte_unificador import (
    UnificadorEstados, 
    CalculadoraDistribuciones, 
    ProcesadorFrases
)


class ServicioUnificador:
    def ejecutar(self, resultados_lista: List[Dict]) -> Dict:
        """
        Orquestador de la unificación de múltiples resultados de apellidos.
        Delega la lógica pesada en clases especializadas de soporte.
        """
        if not resultados_lista:
            return {}
        
        if len(resultados_lista) == 1:
            return resultados_lista[0]
        
        # 1. Unificar Apellidos (Nombres)
        originales = " ".join([r["apellido_original"] for r in resultados_lista])
        normalizados = " ".join([r["apellido_normalizado"] for r in resultados_lista])

        # 2. Resolver Estado Final
        estado_final = UnificadorEstados.resolver_estado(resultados_lista)

        if estado_final == "procesando":
            return self._crear_respuesta_basica(estado_final, originales, normalizados)

        # 3. Procesar Distribuciones (Cálculos y Top 3)
        distribuciones = CalculadoraDistribuciones.calcular(resultados_lista)

        # 4. Procesar Frases (Unificación y Reemplazos Contextuales)
        frases = ProcesadorFrases.unificar(resultados_lista, originales)

        return {
            "estado": estado_final,
            "fuente": "Unificado",
            "apellido_original": originales,
            "apellido_normalizado": normalizados,
            "distribuciones": distribuciones,
            "frases": frases
        }

    def _crear_respuesta_basica(self, estado: str, orig: str, norm: str) -> Dict:
        return {
            "estado": estado,
            "fuente": "Unificado",
            "apellido_original": orig,
            "apellido_normalizado": norm,
            "distribuciones": [],
            "frases": []
        }
