from django.db import transaction
from typing import List, Dict
from app.domain.models.models import Apellido, Departamento, DistribucionApellidoDepartamento, Frases


class PersistenciaApellidoService:
    @transaction.atomic
    def guardar_resultado_completo(self, resultado: Dict):
        """
        Guarda atómicamente un resultado (distribuciones y frases) en la base de datos
        y marca el apellido como LISTO.
        """
        apellido_norm = resultado.get("apellido_normalizado")
        apellido_obj = Apellido.objects.select_for_update().get(apellido=apellido_norm)

        # 1. Guardar Distribuciones
        distribuciones_data = resultado.get("distribuciones", [])
        for dist in distribuciones_data:
            # Manejar si el departamento ya viene como objeto o como dict
            if isinstance(dist.get("departamento"), dict):
                nombre_dept = dist["departamento"]["nombre"]
                frase_dept = dist["departamento"]["frase"]
            else:
                nombre_dept = dist["departamento"].nombre
                frase_dept = dist["departamento"].frase

            departamento_obj, _ = Departamento.objects.get_or_create(
                nombre=nombre_dept,
                defaults={'frase': frase_dept}
            )
            
            DistribucionApellidoDepartamento.objects.get_or_create(
                apellido=apellido_obj,
                departamento=departamento_obj,
                defaults={
                    'porcentaje': dist['porcentaje'],
                    'ranking': dist['ranking'],
                }
            )

        # 2. Guardar Frases
        frases_data = resultado.get("frases", [])
        for f_data in frases_data:
            # Las frases pueden venir de la IA (dict) o ya existir (objetos)
            if isinstance(f_data, dict):
                Frases.objects.get_or_create(
                    categoria=f_data["categoria"],
                    frase=f_data["frase"],
                    apellido=apellido_obj
                )
            # Si f_data fuera un objeto Frases, ya estaría asociado o se ignoraría aquí 
            # ya que el flujo de persistencia se encarga de crear nuevos registros.

        # 3. Finalizar estado
        apellido_obj.estado = Apellido.LISTO
        apellido_obj.fuente = resultado.get("fuente", apellido_obj.fuente)
        apellido_obj.save()

        # Actualizar el objeto resultado con los datos reales de la DB si es necesario
        resultado["distribuciones"] = list(DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj))
        resultado["frases"] = list(Frases.objects.filter(apellido=apellido_obj))
        resultado["estado"] = "encontrado"
