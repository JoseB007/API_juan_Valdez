from typing import List, Dict
import statistics

from app.utils.math import ajustar_porcentaje


class UnificarApellidosService:
    def ejecutar(self, resultados_lista: List[Dict]) -> Dict:
        if not resultados_lista:
            return {}
        
        if len(resultados_lista) == 1:
            return resultados_lista[0]
        
        estados = [r["estado"] for r in resultados_lista]

        if "procesando" in estados:
            estado_unificado = "procesando"
        elif "no_encontrado" in estados:
            estado_unificado = "no_encontrado"
        elif "encontrado" in estados:
            estado_unificado = "encontrado"
        elif "error" in estados:
            estado_unificado = "error"
        else:
            estado_unificado = "procesando"

        # Combinar apellidos
        apellidos_originales = " ".join([r["apellido_original"] for r in resultados_lista])
        apellidos_normalizados = " ".join([r["apellido_normalizado"] for r in resultados_lista])

        if estado_unificado == "procesando":
            return {
                "estado": "procesando",
                "fuente": "Unificado",
                "apellido_original": apellidos_originales,
                "apellido_normalizado": apellidos_normalizados,
                "distribuciones": [],
                "frases": []
            }

        # Agrupar distribuciones por departamento
        dept_data = {}
        for res in resultados_lista:
            if res.get("estado") == "procesando":
                continue

            distribuciones = res.get("distribuciones", [])
            for dist in distribuciones:
                if hasattr(dist, 'departamento'):
                    nombre_dept = dist.departamento.nombre
                    frase_dept = dist.departamento.frase
                    porcentaje = dist.porcentaje
                    ranking = dist.ranking
                else:
                    nombre_dept = dist["departamento"]["nombre"]
                    frase_dept = dist["departamento"]["frase"]
                    porcentaje = dist["porcentaje"]
                    ranking = dist["ranking"]

                if nombre_dept not in dept_data:
                    dept_data[nombre_dept] = {
                        "departamento": {
                            "nombre": nombre_dept,
                            "frase": frase_dept
                        },
                        "porcentajes": [],
                        "rankings": []
                    }
                
                dept_data[nombre_dept]["porcentajes"].append(porcentaje)
                dept_data[nombre_dept]["rankings"].append(ranking)
        
        # Promediar o tomar el valor único
        distribuciones_finales = []
        for nombre, data in dept_data.items():
            avg_porcentaje = statistics.mean(data["porcentajes"])
            avg_ranking = round(statistics.mean(data["rankings"]))
            
            distribuciones_finales.append({
                "departamento": data["departamento"],
                "porcentaje": avg_porcentaje,
                "ranking": avg_ranking
            })

        # Ordenar por porcentaje descendente y tomar los 3 primeros
        distribuciones_finales = sorted(
            distribuciones_finales, 
            key=lambda x: x["porcentaje"], 
            reverse=True
        )[:3]

        # Normalizar porcentajes para que sumen 100%
        if distribuciones_finales:
            total_porcentaje = sum(d["porcentaje"] for d in distribuciones_finales)
            if total_porcentaje > 0:
                for d in distribuciones_finales:
                    d["porcentaje"] = round((d["porcentaje"] / total_porcentaje) * 100)

        # Ajustar porcentajes para que sumen 100%
        distribuciones_finales = ajustar_porcentaje(distribuciones_finales)

        # Combinar frases (sin duplicados exactos)
        frases_finales = self.unificar_frases(apellidos_originales, resultados_lista)

        return {
            "estado": estado_unificado if estado_unificado else resultados_lista[0]["estado"],
            "fuente": "Unificado",
            "apellido_original": apellidos_originales,
            "apellido_normalizado": apellidos_normalizados,
            "distribuciones": distribuciones_finales,
            "frases": frases_finales
        }

    def unificar_frases(self, apellido_unificado: str, resultados_lista: List[Dict]) -> List[Dict]:
        frases_finales = []
        vistas_frases = set()
        
        for res in resultados_lista:
            apellido_individual = res.get("apellido_original", "")
            frases = res.get("frases", [])
            for f in frases:
                if hasattr(f, 'categoria'):
                    cat = f.categoria
                    txt = f.frase
                else:
                    cat = f["categoria"]
                    txt = f["frase"]
                
                # Reemplazar el apellido individual por el unificado
                if apellido_individual and apellido_unificado:
                    txt = txt.replace(apellido_individual, apellido_unificado)
                
                identificador = f"{cat}:{txt}"
                if apellido_unificado in identificador:
                    if identificador not in vistas_frases:
                        frases_finales.append({"categoria": cat, "frase": txt})
                        vistas_frases.add(identificador)
        
        return frases_finales[:4]
