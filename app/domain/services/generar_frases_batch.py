from typing import List, Dict

from app.integrations.ai_cliente import generar_frases_batch_ia


class GenerarFrasesBatchService:
    def ejecutar(self, resultados: List[Dict]) -> List[Dict]:
        """
        Recibe una lista de resultados de apellidos y genera frases en batch
        actualizando los diccionarios en memoria.
        """
        apellidos_para_ia = []
        
        for res in resultados:
            if res.get("estado") == "encontrado" and not res.get("frases"):
                # Necesita frases
                apellido_str = res.get("apellido_original")
                # Obtener distribuciones simplificadas para el prompt
                distribuciones = []
                for dist in res.get("distribuciones", []):
                    # Manejar si el departamento es objeto o dict
                    if hasattr(dist, 'departamento'):
                        nombre_dept = dist.departamento.nombre
                        porcentaje = dist.porcentaje
                    elif isinstance(dist.get("departamento"), dict):
                        nombre_dept = dist["departamento"]["nombre"]
                        porcentaje = dist["porcentaje"]
                    else:
                        nombre_dept = dist["departamento"]
                        porcentaje = dist["porcentaje"]
                    
                    distribuciones.append({
                        "departamento": nombre_dept,
                        "porcentaje": porcentaje
                    })
                
                apellidos_para_ia.append({
                    "apellido": apellido_str,
                    "distribuciones": distribuciones,
                    "resultado_ref": res # Mantener referencia para actualizar luego
                })
        
        if not apellidos_para_ia:
            return resultados

        data_ia = [
            {
                "apellido": item["apellido"], 
                "distribuciones": item["distribuciones"]
            } for item in apellidos_para_ia
        ]
        
        respuesta_ia = generar_frases_batch_ia(data_ia)
        resultados_ia = respuesta_ia.get("resultados", [])
        
        # Crear un mapa para facilitar la búsqueda por apellido ignorando mayúsculas/minúsculas
        mapa_ia = {
            r["apellido"].lower(): r["frases"] for r in resultados_ia
        }
        
        for item in apellidos_para_ia:
            apellido_lower = item["apellido"].lower()
            if apellido_lower in mapa_ia:
                frases_data = mapa_ia[apellido_lower]
                # Guardar solo el formato de diccionario para la persistencia posterior
                item["resultado_ref"]["frases"] = [{
                    "categoria": f["categoria"], 
                    "frase": f["texto"]
                    } for f in frases_data
                ]
                item["resultado_ref"]["nuevo"] = True

        return resultados
