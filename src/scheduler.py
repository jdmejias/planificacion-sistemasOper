import os
import collections
from process import Proceso


class MLFQScheduler:
    def __init__(self, esquema):
        """
        Implementación de un planificador MLFQ (Multilevel Feedback Queue).

        Parámetros:
        - esquema: lista de tuplas (politica, quantum)
          politica: 'RR' (Round Robin), 'SJF' (Shortest Job First), 'STCF' (Shortest Time to Completion First)
          quantum: entero para RR, None para SJF/STCF
        """
        self.esquema = esquema
        # Cada cola depende de la política: si es RR usamos deque (FIFO), si no, una lista normal
        self.colas = [
            collections.deque() if politica == 'RR' else []
            for politica, _ in esquema
        ]
        self.cola_llegadas = []       # Procesos que aún no han llegado al sistema
        self.tiempo_global = 0        # Reloj global de la simulación
        self.procesos_finalizados = []  # Lista de procesos completados

    def agregar_proceso(self, proceso):
        """
        Agrega un proceso al planificador.
        Puede venir como diccionario o como objeto Proceso.
        """
        # Si viene como dict, se convierte a objeto Proceso
        if not isinstance(proceso, Proceso):
            proceso = Proceso(
                pid=proceso['pid'],
                tiempo_rafaga=proceso['burst_time'],
                tiempo_llegada=proceso['arrival_time'],
                nivel_cola=proceso['queue_level'],
                prioridad=proceso['priority']
            )

        # Si aún no ha llegado, lo guardamos en la cola de llegadas
        if proceso.tiempo_llegada > self.tiempo_global:
            self.cola_llegadas.append(proceso)
            # Mantener la cola ordenada por tiempo de llegada
            self.cola_llegadas.sort(key=lambda p: p.tiempo_llegada)
        else:
            # Si ya llegó, lo ponemos directamente en su cola
            self.colas[proceso.nivel_cola].append(proceso)

    def planificar(self):
        """
        Selecciona el próximo proceso a ejecutar de acuerdo al esquema MLFQ.
        Retorna (indice_de_cola, proceso).
        """
        proceso = None
        indice = None
        encontrado = False

        i = 0
        # Buscar la primera cola no vacía
        while i < len(self.colas) and not encontrado:
            cola = self.colas[i]
            if cola:
                politica, quantum = self.esquema[i]
                if politica == 'RR':
                    proceso = cola.popleft()  # Round Robin: primero en entrar, primero en salir
                elif politica in ('SJF', 'STCF'):
                    # Selecciona el proceso con menor tiempo restante
                    clave = lambda p: p.tiempo_restante
                    proceso = min(cola, key=clave)
                    cola.remove(proceso)
                indice = i
                encontrado = True
            i += 1

        return indice, proceso

    def ejecutar(self):
        """
        Ejecuta la simulación del planificador MLFQ hasta que no queden procesos.
        """
        while self.cola_llegadas or any(self.colas):
            # 1) Mover a las colas los procesos cuyo tiempo de llegada ya se cumplió
            while self.cola_llegadas and self.cola_llegadas[0].tiempo_llegada <= self.tiempo_global:
                proceso = self.cola_llegadas.pop(0)
                self.colas[proceso.nivel_cola].append(proceso)

            # 2) Escoger el próximo proceso a ejecutar
            indice, proceso = self.planificar()

            if proceso is not None:
                # Registrar el tiempo de inicio si es la primera vez que se ejecuta
                if proceso.tiempo_inicio is None:
                    proceso.tiempo_inicio = self.tiempo_global

                politica, quantum = self.esquema[indice]
                # Determinar cuánto tiempo va a correr
                if politica == 'RR':
                    tiempo_ejecucion = min(quantum, proceso.tiempo_restante)
                elif politica == 'SJF':
                    tiempo_ejecucion = proceso.tiempo_restante
                else:  # STCF (preemptivo)
                    proxima_llegada = self.cola_llegadas[0].tiempo_llegada if self.cola_llegadas else float('inf')
                    tiempo_ejecucion = min(proceso.tiempo_restante, proxima_llegada - self.tiempo_global)

                # Mostrar en consola el intervalo ejecutado
                inicio = self.tiempo_global
                fin = inicio + tiempo_ejecucion
                print(f"{inicio} a {fin} {proceso.pid}")

                # Avanzar el reloj y reducir tiempo restante
                self.tiempo_global = fin
                proceso.tiempo_restante -= tiempo_ejecucion

                # Si no ha terminado, volver a encolar
                if proceso.tiempo_restante > 0:
                    if politica == 'STCF':
                        # Vuelve a la misma cola
                        self.colas[indice].append(proceso)
                    else:
                        # Baja a la siguiente cola en caso de RR o SJF
                        nuevo_indice = min(indice + 1, len(self.colas) - 1)
                        proceso.nivel_cola = nuevo_indice
                        self.colas[nuevo_indice].append(proceso)
                else:
                    # Si terminó, registramos su finalización
                    proceso.tiempo_finalizacion = self.tiempo_global
                    self.procesos_finalizados.append(proceso)
            else:
                # Si no hay procesos listos, avanzar el tiempo al próximo arribo
                if self.cola_llegadas:
                    self.tiempo_global = self.cola_llegadas[0].tiempo_llegada

    def escribir_salida(self, ruta):
        """
        Escribe en un archivo los resultados de la planificación.
        Incluye métricas promedio y detalle por proceso.
        """
        # Crear carpeta de salida si no existe
        carpeta_salida = os.path.dirname(ruta)
        if carpeta_salida and not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida, exist_ok=True)

        nombre_original = os.path.basename(ruta).replace('_out', '')
        cantidad = len(self.procesos_finalizados)

        # Calcular métricas promedio
        prom_espera = sum(p.tiempo_espera for p in self.procesos_finalizados) / cantidad
        prom_finalizacion = sum(p.tiempo_finalizacion for p in self.procesos_finalizados) / cantidad
        prom_respuesta = sum(p.tiempo_respuesta for p in self.procesos_finalizados) / cantidad
        prom_retorno = sum(p.tiempo_retorno for p in self.procesos_finalizados) / cantidad

        # Guardar resultados en archivo
        with open(ruta, 'w') as archivo:
            archivo.write(f"# archivo: {nombre_original}\n")
            archivo.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")
            for p in sorted(self.procesos_finalizados, key=lambda x: x.pid):
                archivo.write(
                    f"{p.pid};{p.tiempo_rafaga};{p.tiempo_llegada};"
                    f"{p.nivel_cola+1};{p.prioridad};"
                    f"{p.tiempo_espera};{p.tiempo_finalizacion};"
                    f"{p.tiempo_respuesta};{p.tiempo_retorno}\n"
                )
            archivo.write(
                f"WT={prom_espera:.1f};CT={prom_finalizacion:.1f};"
                f"RT={prom_respuesta:.1f};TAT={prom_retorno:.1f};\n"
            )
