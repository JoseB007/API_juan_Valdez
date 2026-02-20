from typing import List, Dict, Set
import statistics
from app.utils.math import ajustar_porcentaje


class UnificadorEstados:
    """Resuelve el estado final basado en la jerarquía de una lista de resultados."""
    
    @staticmethod
    def resolver_estado(resultados: List[Dict]) -> str:
        if not resultados:
            return "procesando"
            
        estados = [r.get("estado") for r in resultados]
        
        if "procesando" in estados:
            return "procesando"
        if "no_encontrado" in estados:
            return "no_encontrado"
        if "encontrado" in estados:
            return "encontrado"
        if "error" in estados:
            return "error"
            
        return "procesando"


class CalculadoraDistribuciones:
    """Maneja la lógica matemática de agrupar y promediar distribuciones territoriales."""
    
    @staticmethod
    def calcular(resultados: List[Dict]) -> List[Dict]:
        dept_data = {}
        
        for res in resultados:
            if res.get("estado") == "procesando":
                continue

            for dist in res.get("distribuciones", []):
                # Estandarizar acceso a datos (soporta objeto o dict)
                nombre, frase, porcentaje, ranking = CalculadoraDistribuciones._extraer_datos_dist(dist)

                if nombre not in dept_data:
                    dept_data[nombre] = {
                        "departamento": {
                            "nombre": nombre, 
                            "frase": frase
                        },
                        "porcentajes": [],
                        "rankings": []
                    }
                
                dept_data[nombre]["porcentajes"].append(porcentaje)
                dept_data[nombre]["rankings"].append(ranking)
        
        return CalculadoraDistribuciones._procesar_final(dept_data)

    @staticmethod
    def _extraer_datos_dist(dist):
        if hasattr(dist, 'departamento'):
            return (
                dist.departamento.nombre,
                dist.departamento.frase,
                float(dist.porcentaje),
                int(dist.ranking)
            )
        return (
            dist["departamento"]["nombre"],
            dist["departamento"]["frase"],
            float(dist["porcentaje"]),
            int(dist["ranking"])
        )

    @staticmethod
    def _procesar_final(dept_data: Dict) -> List[Dict]:
        finales = []
        for nombre, data in dept_data.items():
            finales.append({
                "departamento": data["departamento"],
                "porcentaje": statistics.mean(data["porcentajes"]),
                "ranking": round(statistics.mean(data["rankings"]))
            })

        # Tomar Top 3 por porcentaje descendente e igualar a 100%
        finales = sorted(finales, key=lambda x: x["porcentaje"], reverse=True)[:3]
        
        if finales:
            total = sum(d["porcentaje"] for d in finales)
            if total > 0:
                for d in finales:
                    d["porcentaje"] = round((d["porcentaje"] / total) * 100)
            finales = ajustar_porcentaje(finales)
            
        return finales


class ProcesadorFrases:
    """Maneja la combinación y limpieza lingüística de frases."""
    
    @staticmethod
    def unificar(resultados: List[Dict], apellido_unificado: str) -> List[Dict]:
        finales = []
        vistas: Set[str] = set()
        
        for res in resultados:
            individual = res.get("apellido_original", "")
            for f in res.get("frases", []):
                cat, txt = ProcesadorFrases._extraer_frase(f)
                
                # Reemplazo contextual del apellido
                if individual and apellido_unificado:
                    txt = txt.replace(individual, apellido_unificado)
                
                id_unico = f"{cat}:{txt}"
                # Solo incluimos si el apellido unificado está en el texto y no es repetida
                if apellido_unificado in id_unico and id_unico not in vistas:
                    finales.append({"categoria": cat, "frase": txt})
                    vistas.add(id_unico)
        
        return finales[:4]

    @staticmethod
    def _extraer_frase(f):
        if hasattr(f, 'categoria'):
            return f.categoria, f.frase
        return f["categoria"], f["frase"]
