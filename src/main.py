import sys
import os
from scheduler import MLFQScheduler

def leer_entrada(ruta_archivo):
    """Lee el archivo de entrada y retorna la lista de procesos."""
    procesos = []
    with open(ruta_archivo) as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea and not linea.startswith('#'):
                partes = [x.strip() for x in linea.split(';')]

                # Ajusta según si tienes prioridad o no en el archivo
                if len(partes) == 5:
                    pid, bt, at, nivel_cola, prioridad = partes
                else:
                    pid, bt, at, nivel_cola = partes
                    prioridad = 0

                procesos.append({
                    'pid': pid,
                    'burst_time': int(bt),
                    'arrival_time': int(at),
                    'queue_level': int(nivel_cola) - 1,
                    'priority': int(prioridad)
                })
    return procesos


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo_entrada>")
        sys.exit(1)

    archivo_entrada = sys.argv[1]
    if not os.path.exists(archivo_entrada):
        ruta_alternativa = os.path.join(
            os.path.dirname(__file__), '..', 'input', archivo_entrada
        )
        if os.path.exists(ruta_alternativa):
            archivo_entrada = ruta_alternativa
        else:
            print(f"Archivo {archivo_entrada} no encontrado.")
            sys.exit(1)

    procesos = leer_entrada(archivo_entrada)

    # Esquemas disponibles
    esquema1 = [('RR', 1), ('RR', 3), ('RR', 4), ('SJF', None)]
    esquema2 = [('RR', 2), ('RR', 3), ('RR', 4), ('STCF', None)]
    esquema3 = [('RR', 3), ('RR', 5), ('RR', 6), ('RR', 20)]

    # Selección de esquema (ejemplo: usar esquema1)
    planificador = MLFQScheduler(esquema1)
    for proceso in procesos:
        planificador.agregar_proceso(proceso)

    planificador.ejecutar()

    # Construir nombre de salida
    archivo_salida = archivo_entrada.replace('input', 'output').replace('.txt', '_out.txt')
    planificador.escribir_salida(archivo_salida)

    print("✅ Salida escrita en:", archivo_salida)


if __name__ == '__main__':
    main()
