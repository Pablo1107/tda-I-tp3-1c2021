#!/usr/bin/env python3
import sys
from grafo import Grafo, Bellman_Ford, Ford_Fulkerson, Cycle_Cancelling

def leer_grafo(nombre_fichero):
    """
    Lee un grafo a partir de un fichero de texto.
    Devuelve un objeto de clase Grafo
    """
    
    with open(nombre_fichero, 'r') as f:
        fuente = f.readline().rstrip()
        sumidero = f.readline().rstrip()
        grafo = Grafo(fuente, sumidero)
        
        for linea in f:
            linea = linea.rstrip()
            origen, destino, costo, capacidad = linea.split(',')
            atributos = {'costo': int(costo), 'capacidad': int(capacidad)}
            grafo.agregar_arista(origen, destino, atributos)

        return grafo

def main(nombre_fichero):
    grafo = leer_grafo(nombre_fichero)
    # print(grafo)
    # grafo.DFS(grafo.fuente)
    grafo_residual, flujo = Ford_Fulkerson(grafo)
    grafo_final, costo = Cycle_Cancelling(grafo, grafo_residual)
    print('La cantdad maxima de personas que pueden viajar es: ' , flujo)
    print('El costo de todos los viajes es: ', costo)
    
    
    # res = Bellman_Ford(grafo, grafo.fuente)
    # if res:
    #     ciclos, costo = res
    #     ciclos = ','.join(ciclos)
    #     print(f'Existen al menos un ciclo negativo en el grafo. {ciclos} → costo: {costo}')
    # else: 
    #     print('No existen ciclos negativos en el grafo')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {} <filename>'.format(sys.argv[0]))
        sys.exit(1)

    main(sys.argv[1])
