import sys
import os
from scheduler import MLFQScheduler

def leer_entrada(ruta_archivo):
    """Lee el archivo de entrada y retorna la lista de procesos como diccionarios."""
    procesos = []
    with open(ruta_archivo) as archivo:
        for linea in archivo:
            linea = linea.strip()
            # Ignorar líneas vacías o comentarios
            if linea and not linea.startswith('#'):
                partes = [x.strip() for x in linea.split(';')]

                # Si el archivo trae prioridad, usarla; si no, poner 0 por defecto
                if len(partes) == 5:
                    pid, bt, at, nivel_cola, prioridad = partes
                else:
                    pid, bt, at, nivel_cola = partes
                    prioridad = 0

                # Guardar proceso en forma de diccionario
                procesos.append({
                    'pid': pid,
                    'burst_time': int(bt),          # tiempo de ráfaga
                    'arrival_time': int(at),        # tiempo de llegada
                    'queue_level': int(nivel_cola) - 1,  # nivel de cola (ajustado a índice)
                    'priority': int(prioridad)      # prioridad (si aplica)
                })
    return procesos


def main():
    # Verificación de argumentos
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo_entrada>")
        sys.exit(1)

    archivo_entrada = sys.argv[1]

    # Buscar el archivo de entrada (directo o en carpeta 'input')
    if not os.path.exists(archivo_entrada):
        ruta_alternativa = os.path.join(
            os.path.dirname(__file__), '..', 'input', archivo_entrada
        )
        if os.path.exists(ruta_alternativa):
            archivo_entrada = ruta_alternativa
        else:
            print(f"Archivo {archivo_entrada} no encontrado.")
            sys.exit(1)

    # Leer procesos del archivo
    procesos = leer_entrada(archivo_entrada)

    # Esquemas de planificación disponibles
    esquema1 = [('RR', 1), ('RR', 3), ('RR', 4), ('SJF', None)]
    esquema2 = [('RR', 2), ('RR', 3), ('RR', 4), ('STCF', None)]
    esquema3 = [('RR', 3), ('RR', 5), ('RR', 6), ('RR', 20)]

    # Selección de esquema (por defecto: esquema1)
    planificador = MLFQScheduler(esquema1)

    # Agregar procesos al planificador
    for proceso in procesos:
        planificador.agregar_proceso(proceso)

    # Ejecutar la planificación
    planificador.ejecutar()

    # Construcción del nombre del archivo de salida
    archivo_salida = archivo_entrada.replace('input', 'output').replace('.txt', '_out.txt')

    # Escribir resultados en archivo
    planificador.escribir_salida(archivo_salida)

    print("✅ Salida escrita en:", archivo_salida)


if __name__ == '__main__':
    main()
