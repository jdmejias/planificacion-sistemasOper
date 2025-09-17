class Proceso:
    def __init__(self, pid, tiempo_rafaga, tiempo_llegada=0, nivel_cola=0, prioridad=0):
        """
        Representa un proceso dentro del planificador MLFQ.

        Parámetros:
        - pid: identificador único del proceso
        - tiempo_rafaga: tiempo total de CPU que requiere
        - tiempo_llegada: instante en que el proceso entra al sistema
        - nivel_cola: nivel inicial dentro de la cola MLFQ
        - prioridad: valor de prioridad (si aplica en el esquema)
        """
        self.pid = pid
        self.tiempo_rafaga = tiempo_rafaga                # Tiempo total de ejecución requerido
        self.tiempo_restante = tiempo_rafaga              # Tiempo de CPU que aún le falta
        self.tiempo_llegada = tiempo_llegada              # Tiempo de llegada al sistema
        self.nivel_cola = nivel_cola                      # Nivel de la cola en el planificador
        self.prioridad = prioridad                        # Prioridad del proceso
        self.tiempo_inicio = None                         # Momento en que empieza a ejecutarse
        self.tiempo_finalizacion = None                   # Momento en que termina su ejecución

    @property
    def tiempo_espera(self):
        """
        Tiempo que el proceso pasó esperando en las colas
        (tiempo total en el sistema - tiempo en CPU).
        """
        resultado = None
        if self.tiempo_finalizacion is not None:
            resultado = self.tiempo_finalizacion - self.tiempo_llegada - self.tiempo_rafaga
        return resultado

    @property
    def tiempo_retorno(self):
        """
        Tiempo de retorno (turnaround time): desde que llega el proceso
        hasta que finaliza completamente.
        """
        resultado = None
        if self.tiempo_finalizacion is not None:
            resultado = self.tiempo_finalizacion - self.tiempo_llegada
        return resultado

    @property
    def tiempo_respuesta(self):
        """
        Tiempo de respuesta: diferencia entre el instante de llegada
        y el momento en que empezó a ejecutarse por primera vez.
        """
        resultado = None
        if self.tiempo_inicio is not None:
            resultado = self.tiempo_inicio - self.tiempo_llegada
        return resultado
