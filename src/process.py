class Proceso:
    def __init__(self, pid, tiempo_rafaga, tiempo_llegada=0, nivel_cola=0, prioridad=0):
        self.pid = pid
        self.tiempo_rafaga = tiempo_rafaga
        self.tiempo_restante = tiempo_rafaga
        self.tiempo_llegada = tiempo_llegada
        self.nivel_cola = nivel_cola
        self.prioridad = prioridad
        self.tiempo_inicio = None
        self.tiempo_finalizacion = None

    @property
    def tiempo_espera(self):
        resultado = None
        if self.tiempo_finalizacion is not None:
            resultado = self.tiempo_finalizacion - self.tiempo_llegada - self.tiempo_rafaga
        return resultado

    @property
    def tiempo_retorno(self):
        resultado = None
        if self.tiempo_finalizacion is not None:
            resultado = self.tiempo_finalizacion - self.tiempo_llegada
        return resultado

    @property
    def tiempo_respuesta(self):
        resultado = None
        if self.tiempo_inicio is not None:
            resultado = self.tiempo_inicio - self.tiempo_llegada
        return resultado
