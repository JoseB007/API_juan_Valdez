import time
from typing import List, Dict
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor

from app.domain.models.models import DistribucionApellidoDepartamento, Apellido, Frases
from app.domain.services.obtener_apellido_IA import ObtenerApellidoIA
from app.domain.services.obtener_apellido_API_ONOGRAPG import ObtenerApellidoAPIOnograph
from app.domain.services.unificar_apellidos import UnificarApellidosService
from app.domain.services.apellido_no_encontrado import apellido_no_encontrado
from app.domain.services.generar_frases_batch import GenerarFrasesBatchService
from app.domain.services.persistencia_apellido import PersistenciaApellidoService


class ServicioProcesarMultiplesApellidos:
    def ejecutar(self, lista_apellidos: List[str], lista_originales: List[str]) -> Dict:
        """
        Coordina la obtención de información para múltiples apellidos:
        1. Obtiene distribuciones (in-memory o DB).
        2. Verifica si alguno está procesando.
        3. Genera frases en batch (in-memory).
        4. Persiste los resultados nuevos de forma atómica.
        5. Unifica los resultados.
        """
        # 1. Obtención de distribuciones
        # resultados = []
        # for norm, orig in zip(lista_apellidos, lista_originales):
        #     info_apellido = obtener_informacion_apellido(norm, orig)
        #     resultados.append(info_apellido)

        # 1. Obtención de distribuciones en paralelo
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(obtener_informacion_apellido, norm, orig)
                for norm, orig in zip(lista_apellidos, lista_originales)
            ]

            resultados = [f.result() for f in futures]

        # 2. Verificar estado procesando
        unificador = UnificarApellidosService()
        if any(r["estado"] == "procesando" for r in resultados):
           return unificador.ejecutar(resultados)
        
        # 3. Generación de frases en batch (actualiza resultados en memoria)
        generador_frases = GenerarFrasesBatchService()
        resultados = generador_frases.ejecutar(resultados)

        # 4. Persistencia de resultados nuevos
        persistencia = PersistenciaApellidoService()
        for res in resultados:
            if res.get("nuevo"):
                persistencia.guardar_resultado_completo(res)

        # 5. Unificación final    
        return unificador.ejecutar(resultados)


def obtener_informacion_apellido(apellido_normalizado: str, apellido_original: str) -> Dict:
    with transaction.atomic():
        apellido_obj, created = Apellido.objects.get_or_create(
            apellido=apellido_normalizado,
            defaults={'estado': Apellido.PENDIENTE, 'fuente': 'Buscando...'}
        )

        # Bloqueamos el registro para evitar que otros procesos lo modifiquen simultáneamente
        apellido_obj = Apellido.objects.select_for_update().get(pk=apellido_obj.pk)

        if not created:
            if apellido_obj.estado == Apellido.LISTO:
                distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
                frases = Frases.objects.filter(apellido=apellido_obj)

                return {
                    "estado": "encontrado",
                    "fuente": apellido_obj.fuente,
                    "apellido_original": apellido_original,
                    "apellido_normalizado": apellido_obj.apellido,
                    "distribuciones": list(distribuciones),
                    "frases": list(frases)
                }
            
            # Verificamos si el proceso está "atascado" (más de 5 minutos en PENDIENTE)
            esta_caducado = (timezone.now() - apellido_obj.created_at) > timedelta(minutes=1)
            
            if apellido_obj.estado == Apellido.PENDIENTE and not esta_caducado:
                return {
                    "estado": "procesando",
                    "fuente": "",
                    "apellido_original": apellido_original,
                    "apellido_normalizado": apellido_normalizado,
                    "distribuciones": [],
                    "frases": []
                }
            
            # Reiniciar si falló o caducó
            Apellido.objects.filter(pk=apellido_obj.pk).update(
                estado=Apellido.PENDIENTE, 
                created_at=timezone.now()
            )

    try:
        # Intento con Onograph (Retorna datos en memoria)
        servicio = ObtenerApellidoAPIOnograph(apellido_normalizado, apellido_original)
        resultado = servicio.ejecutar()

        if resultado.get('estado') == "encontrado":
            return resultado

        # Si no se encuentra, se recurre a la IA
        if resultado.get('estado') == "no_encontrado":
            servicio_ia = ObtenerApellidoIA(apellido_normalizado, apellido_original)
            return servicio_ia.ejecutar()

        return resultado
    except Exception as e:
        Apellido.objects.filter(apellido=apellido_normalizado).update(estado=Apellido.FALLIDO)
        raise e


def consultar_estado_apellido(apellido_normalizado: str, apellido_original: str) -> Dict:
    try:
        apellido_obj = Apellido.objects.get(apellido=apellido_normalizado)
        
        if apellido_obj.estado == Apellido.LISTO:
            distribuciones = DistribucionApellidoDepartamento.objects.filter(apellido=apellido_obj)
            frases = Frases.objects.filter(apellido=apellido_obj)

            return {
                "estado": "encontrado",
                "fuente": apellido_obj.fuente,
                "apellido_original": apellido_original,
                "apellido_normalizado": apellido_obj.apellido,
                "distribuciones": list(distribuciones),
                "frases": list(frases)
            }
        
        if apellido_obj.estado == Apellido.PENDIENTE:
            return {
                "estado": "procesando",
                "fuente": "",
                "apellido_original": apellido_original,
                "apellido_normalizado": apellido_normalizado,
                "distribuciones": [],
                "frases": []
            }
        
        return {
            "estado": "error",
            "fuente": "",
            "apellido_original": apellido_original,
            "apellido_normalizado": apellido_normalizado,
            "distribuciones": [],
            "frases": [],
        }
        
    except Apellido.DoesNotExist:
        return apellido_no_encontrado(apellido_original, apellido_normalizado)