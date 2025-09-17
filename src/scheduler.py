import os
import collections
from process import Proceso


class MLFQScheduler:
    def __init__(self, esquema):
        """
        esquema: lista de (politica, quantum)
          politica: 'RR', 'SJF', 'STCF'
          quantum: int para RR, None para SJF/STCF
        """
        self.esquema = esquema
        self.colas = [
            collections.deque() if politica == 'RR' else []
            for politica, _ in esquema
        ]
        self.cola_llegadas = []       # procesos aún no han llegado
        self.tiempo_global = 0
        self.procesos_finalizados = []

    def agregar_proceso(self, proceso):
            # Si viene un dict, mapéalo a los parámetros que Proceso espera
            if not isinstance(proceso, Proceso):
                proceso = Proceso(
                    pid=proceso['pid'],
                    tiempo_rafaga=proceso['burst_time'],
                    tiempo_llegada=proceso['arrival_time'],
                    nivel_cola=proceso['queue_level'],
                    prioridad=proceso['priority']
                )
            # Ahora sí encolamos según tiempo de llegada
            if proceso.tiempo_llegada > self.tiempo_global:
                self.cola_llegadas.append(proceso)
                self.cola_llegadas.sort(key=lambda p: p.tiempo_llegada)
            else:
                self.colas[proceso.nivel_cola].append(proceso)
    def planificar(self):
        proceso = None
        indice = None
        encontrado = False

        i = 0
        while i < len(self.colas) and not encontrado:
            cola = self.colas[i]
            if cola:
                politica, quantum = self.esquema[i]
                if politica == 'RR':
                    proceso = cola.popleft()
                elif politica in ('SJF', 'STCF'):
                    clave = lambda p: p.tiempo_restante
                    proceso = min(cola, key=clave)
                    cola.remove(proceso)
                indice = i
                encontrado = True
            i += 1

        return indice, proceso

    def ejecutar(self):
        # mientras queden procesos por llegar o en colas
        while self.cola_llegadas or any(self.colas):
            # 1) Mover procesos que ya llegaron
            while self.cola_llegadas and self.cola_llegadas[0].tiempo_llegada <= self.tiempo_global:
                proceso = self.cola_llegadas.pop(0)
                self.colas[proceso.nivel_cola].append(proceso)

            # 2) Escoger siguiente proceso
            indice, proceso = self.planificar()

            if proceso is not None:
                if proceso.tiempo_inicio is None:
                    proceso.tiempo_inicio = self.tiempo_global

                politica, quantum = self.esquema[indice]
                if politica == 'RR':
                    tiempo_ejecucion = min(quantum, proceso.tiempo_restante)
                elif politica == 'SJF':
                    tiempo_ejecucion = proceso.tiempo_restante
                else:  # STCF
                    proxima_llegada = self.cola_llegadas[0].tiempo_llegada if self.cola_llegadas else float('inf')
                    tiempo_ejecucion = min(proceso.tiempo_restante, proxima_llegada - self.tiempo_global)

                # Debug en consola: “inicio a fin PID”
                inicio = self.tiempo_global
                fin = inicio + tiempo_ejecucion
                print(f"{inicio} a {fin} {proceso.pid}")

                # avanzar reloj y decrementar tiempo restante
                self.tiempo_global = fin
                proceso.tiempo_restante -= tiempo_ejecucion

                if proceso.tiempo_restante > 0:
                    if politica == 'STCF':
                        self.colas[indice].append(proceso)
                    else:
                        nuevo_indice = min(indice + 1, len(self.colas) - 1)
                        proceso.nivel_cola = nuevo_indice
                        self.colas[nuevo_indice].append(proceso)
                else:
                    proceso.tiempo_finalizacion = self.tiempo_global
                    self.procesos_finalizados.append(proceso)
            else:
                # no hay proceso listo: saltar al tiempo del próximo arribo
                if self.cola_llegadas:
                    self.tiempo_global = self.cola_llegadas[0].tiempo_llegada

    def escribir_salida(self, ruta):
        # asegurar carpeta de salida
        carpeta_salida = os.path.dirname(ruta)
        if carpeta_salida and not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida, exist_ok=True)

        nombre_original = os.path.basename(ruta).replace('_out', '')
        cantidad = len(self.procesos_finalizados)

        prom_espera = sum(p.tiempo_espera for p in self.procesos_finalizados) / cantidad
        prom_finalizacion = sum(p.tiempo_finalizacion for p in self.procesos_finalizados) / cantidad
        prom_respuesta = sum(p.tiempo_respuesta for p in self.procesos_finalizados) / cantidad
        prom_retorno = sum(p.tiempo_retorno for p in self.procesos_finalizados) / cantidad

        with open(ruta, 'w') as archivo:
            archivo.write(f"# archivo: {nombre_original}\n")
            archivo.write("# PID; TR; TL; NC; Pr; TE; TF; TRP; TAT\n")
            for p in sorted(self.procesos_finalizados, key=lambda x: x.pid):
                archivo.write(f"{p.pid}; {p.tiempo_rafaga}; {p.tiempo_llegada}; "
                              f"{p.nivel_cola+1}; {p.prioridad}; "
                              f"{p.tiempo_espera}; {p.tiempo_finalizacion}; "
                              f"{p.tiempo_respuesta}; {p.tiempo_retorno}\n")
            archivo.write(f"TE={prom_espera:.1f}; TF={prom_finalizacion:.1f}; "
                          f"TRP={prom_respuesta:.1f}; TAT={prom_retorno:.1f};\n")
