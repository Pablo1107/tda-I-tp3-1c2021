#!/usr/bin/env python3
import sys
import graphviz
import parte_1

def main(nombre_archivo):
    grafo, grafo_residual = parte_1.main(nombre_archivo)

    dot = graphviz.Digraph(comment='Grafo', format='svg', graph_attr={'rankdir': 'LR' })

    dot.node(grafo.fuente, color='green', rank='source')
    dot.node(grafo.sumidero, color='green', rank='sink')

    for u, v, atributos in grafo:
        costo = atributos['costo']
        capacidad = atributos['capacidad']

        dot.edge(u, v, label=str(costo))

    for u, v, atributos in grafo_residual:
        flujo = atributos['flujo']
        dot.edge(u, v, label=str(flujo), color='red')

    dot.view()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {} <filename>'.format(sys.argv[0]))
        sys.exit(1)

    main(sys.argv[1])
