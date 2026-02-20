import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

from app.domain.models.apellido_models import DistribucionApellidoDepartamento, Apellido, Frases
from app.domain.services.clientes.generacion_ia import ServicioIA
from app.domain.services.clientes.onograph import ServicioOnograph
from app.domain.services.nucleo.unificador import ServicioUnificador
from app.domain.services.casos_especiales import apellido_no_encontrado
from app.domain.services.clientes.frases_batch import ServicioFrasesBatch
from app.domain.services.nucleo.persistencia import ServicioPersistencia
from app.domain.services.nucleo.soporte import ApellidoRepository, ApellidoPolicy


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
        # 1. Obtención de distribuciones en paralelo
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(obtener_informacion_apellido, norm, orig)
                for norm, orig in zip(lista_apellidos, lista_originales)
            ]

            resultados = [f.result() for f in futures]

        # 2. Verificar estado procesando
        unificador = ServicioUnificador()
        if any(r["estado"] == "procesando" for r in resultados):
           return unificador.ejecutar(resultados)
        
        # 3. Generación de frases en batch (actualiza resultados en memoria)
        generador_frases = ServicioFrasesBatch()
        resultados = generador_frases.ejecutar(resultados)

        # 4. Persistencia de resultados nuevos
        persistencia = ServicioPersistencia()
        for res in resultados:
            if res.get("nuevo"):
                persistencia.guardar_resultado_completo(res)

        # 5. Unificación final    
        return unificador.ejecutar(resultados)


def obtener_informacion_apellido(apellido_normalizado: str, apellido_original: str) -> Dict:
    # 1. Obtencion/Creacion inicial con bloqueo
    apellido_obj, created = ApellidoRepository.obtener_o_crear_inicial(apellido_normalizado)

    # 2. Verificar si ya se esta procesando activamente (solo si no es nuevo)
    if not created and ApellidoPolicy.esta_procesando(apellido_obj):
        return {
            "estado": "procesando",
            "fuente": "",
            "apellido_original": apellido_original,
            "apellido_normalizado": apellido_normalizado,
            "distribuciones": [],
            "frases": []
        }

    # 3. Cargar datos existentes y verificar completitud
    datos_db = ApellidoRepository.obtener_datos_completos(apellido_obj)
    
    if datos_db["tiene_distribuciones"]:
        if datos_db["tiene_frases"]:
            ApellidoRepository.marcar_como_listo(apellido_obj)
        
        return {
            "estado": "encontrado",
            "fuente": apellido_obj.fuente or "Cargado de DB",
            "apellido_original": apellido_original,
            "apellido_normalizado": apellido_obj.apellido,
            "distribuciones": datos_db["distribuciones"],
            "frases": datos_db["frases"]
        }

    # 4. Si no hay datos, reiniciar estado e intentar servicios externos
    ApellidoRepository.reiniciar_estado_pendiente(apellido_obj)
    
    try:
        # Intento con Onograph
        servicio = ServicioOnograph(apellido_normalizado, apellido_original)
        resultado = servicio.ejecutar()

        if resultado.get('estado') == "encontrado":
            return resultado

        # Si no se encuentra, se recurre a la IA
        if resultado.get('estado') == "no_encontrado":
            servicio_ia = ServicioIA(apellido_normalizado, apellido_original)
            return servicio_ia.ejecutar()

        return resultado
    except Exception as e:
        ApellidoRepository.marcar_como_fallido(apellido_normalizado)
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
