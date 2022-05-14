from collections import defaultdict,deque
import json



class GrafoIter:
    def __init__(self, grafo):
        self.grafo = grafo
        self.vertices = iter(grafo.vertices)
        self.origen_actual = next(self.vertices)
        self.adyacentes = iter(grafo.adyacentes(self.origen_actual))

    def __next__(self):
        try:
            destino_actual = next(self.adyacentes)
            return self.origen_actual, destino_actual, self.grafo.atributos(self.origen_actual, destino_actual)
        except StopIteration:
            self.origen_actual = next(self.vertices)
            self.adyacentes = iter(self.grafo.adyacentes(self.origen_actual))
            return self.__next__()

class Grafo:
    def __init__(self, fuente, sumidero):
        self.fuente = fuente
        self.sumidero = sumidero
        self._grafo = defaultdict(lambda: defaultdict(dict))
        self.vertices = set()

    def agregar_arista(self, origen, destino, atributos):
        self.vertices.add(origen)
        self.vertices.add(destino)
        self._grafo[origen][destino] = atributos

    def adyacentes(self, vertice):
        """Devuelve una lista de los vertices adyacentes a un vertice"""
        return self._grafo[vertice].keys()

    def atributos(self, origen, destino):
        return self._grafo[origen][destino]

    def BFS(self, origen, destino = None):
        if origen not in self.vertices:
            return None
        if destino != None and destino not in self.vertices:
            return None
        visitados = set()
        padres = {}
        padres[origen] = None
        visitados.add(origen)
        q = deque()
        q.append(origen)
        while not len(q) == 0:
            v = q.pop()
            for w in self._grafo[v]:
                if w not in visitados:
                    padres[w] = v
                    visitados.add(w)
                    q.appendleft(w)
                    if w == destino:
                        return padres
        return padres

    def DFS(self, vertice, f=None, ctx=None):
        if vertice not in self._grafo:
            return

        if not f:
            f = lambda x, _: print(x)

        visitados = set()
        pila = [vertice]
        while pila:
            vertice = pila.pop()
            f(vertice, ctx)
            if vertice not in visitados:
                visitados.add(vertice)
                for v in self.adyacentes(vertice):
                    pila.append(v)

    def __iter__(self):
        return GrafoIter(self)

    def __str__(self):
        return "{}(fuente: '{}', sumidero: '{}', adyacencias: {})".format(
            self.__class__.__name__,
            self.fuente,
            self.sumidero,
            # dict(self._grafo)
            # string of dict with json indent
            json.dumps(dict(self._grafo), indent=4)
        )

    
def Bellman_Ford(grafo, origen):                                      # O(V * E)
    dist = {}
    predecesores = {}

    # Inicializar distancias en infinito
    for v in grafo.vertices:
        dist[v] = float("inf") 

    # Inicializar distancias al origen en cero y 
    dist[origen] = 0
    predecesores[origen] = None

    # Ejecutar por cada vertice
    for _ in grafo.vertices:
        cambio = False
        for v, w, atributos in grafo:
            peso = atributos['costo']
            if dist[v] + peso < dist[w]:
                cambio = True
                predecesores[w] = v
                dist[w] = dist[v] + peso

        if not cambio:
            return dist, predecesores

    # Chequear si hay ciclos negativos
    # y calcular dicho ciclo y su peso
    ciclo = []
    peso_ciclo = 0
    for v, w, atributos in grafo:
        peso = atributos['costo']
        if dist[v] + peso < dist[w]:
            ciclo.append(v)
            arista_actual = v
            predecesor = predecesores[v]
            peso_ciclo = grafo.peso(predecesor, arista_actual)

            while predecesor != v:
                ciclo.append(predecesor)
                arista_actual = predecesor
                predecesor = predecesores[predecesor]
                peso_actual = grafo.peso(predecesor, arista_actual)
                peso_ciclo += peso_actual

            return ciclo[::-1], peso_ciclo

    return dist, predecesores

def camino_fuente_sumidero(grafo_residual):
    """
    Devuelve una lista de aristas que representan el camino de fuente a sumidero

    Ese camino response a cf(u,v) = c(u,v) - f(u,v) y cf(u,v) > 0

    """
    camino = []

    # Buscar el camino de fuente a sumidero con BFS
    predecesores = grafo_residual.BFS(grafo_residual.fuente, grafo_residual.sumidero)

    # Reconstruir camino del sumidero a la fuente
    actual = grafo_residual.sumidero
    while actual != grafo_residual.fuente:
        if actual not in predecesores:
            return None
        predecesor = predecesores[actual]

        camino.append((predecesor, actual, grafo_residual._grafo[predecesor][actual]['capacidad']))
        actual = predecesor
    camino.reverse()
    return camino

def Ford_Fulkerson(grafo):
    flujo_maximo = 0
    grafo_residual = Grafo(grafo.fuente, grafo.sumidero)

    for u, v, _ in grafo:
        grafo_residual.agregar_arista(u, v, {'capacidad': grafo.atributos(u,v)['capacidad']})

    while camino := camino_fuente_sumidero(grafo_residual):
        capacidad_maxima = min(capacidad for u, v, capacidad in camino)
        flujo_maximo += capacidad_maxima
        for u, v, _ in camino:
            if u not in grafo_residual.adyacentes(v):
                grafo_residual.agregar_arista(v, u, {'capacidad': 0})
            grafo_residual._grafo[v][u]['capacidad'] += capacidad_maxima

            grafo_residual._grafo[u][v]['capacidad'] -= capacidad_maxima
            if grafo_residual._grafo[u][v]['capacidad'] == 0:
                del(grafo_residual._grafo[u][v])

    return (grafo_residual)


def Cycle_Cancelling(grafo):
    pass
