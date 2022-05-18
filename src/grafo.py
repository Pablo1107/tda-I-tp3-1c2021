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
        if (
            origen not in self._grafo.keys() or
            destino not in self._grafo[origen].keys()
        ): return None

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

    
def Bellman_Ford(grafo):                                      # O(V * E)
    dist = {}
    predecesores = {}

    # Inicializar distancias en infinito
    for v in grafo.vertices:
        dist[v] = float("inf") 

    # Inicializar distancias al origen en cero y 
    dist[grafo.sumidero] = 0
    predecesores[grafo.sumidero] = None

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
            return

    # Chequear si hay ciclos negativos
    # y calcular dicho ciclo y su peso
    ciclo = []
    peso_ciclo = 0
    visitados = set()
    for v, w, atributos in grafo:
        peso = atributos['costo']
        if dist[v] + peso < dist[w]:
            visitados.add(v)            
            predecesor = predecesores[v]

            while predecesor not in visitados:
                visitados.add(predecesor)
                predecesor = predecesores[predecesor]

            primer = predecesor 
            actual = primer
            predecesor = predecesores[predecesor]
            ciclo.append((predecesor, actual, grafo.atributos(predecesor, actual)['capacidad']))

            while predecesor != primer:        
                actual = predecesor
                predecesor = predecesores[predecesor]
                peso_actual = grafo.atributos(predecesor, actual)['capacidad']
                peso_ciclo += peso_actual
                ciclo.append((predecesor, actual, grafo.atributos(predecesor, actual)['capacidad']))
            return ciclo[::-1]
    return

def camino_fuente_sumidero(grafo):
    """
    Devuelve una lista de aristas que representan el camino de fuente a sumidero

    Ese camino response a cf(u,v) = c(u,v) - f(u,v) y cf(u,v) > 0

    """
    camino = []

    # Buscar el camino de fuente a sumidero con BFS
    predecesores = grafo.BFS(grafo.fuente, grafo.sumidero)

    # Reconstruir camino del sumidero a la fuente
    actual = grafo.sumidero
    while actual != grafo.fuente:
        if actual not in predecesores:
            return None
        predecesor = predecesores[actual]

        camino.append((predecesor, actual, grafo._grafo[predecesor][actual]['capacidad']))
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

    return grafo_residual, flujo_maximo

def Cycle_Cancelling(grafo, grafo_residual):
    for (u, v, _) in grafo_residual:
        if v not in grafo._grafo[u]:
            grafo_residual._grafo[u][v]['costo'] = -grafo.atributos(v,u)['costo']
        else:
            grafo_residual._grafo[u][v]['costo'] = grafo.atributos(u,v)['costo']

    while ciclo := Bellman_Ford(grafo_residual):
        bottleneck = min(capacidad for u, v, capacidad in ciclo)
        for u, v, _ in ciclo:
            if u not in grafo_residual.adyacentes(v):
                grafo_residual.agregar_arista(v, u, {'capacidad': 0, 'costo': 0})
                if u not in grafo._grafo[v]:
                    grafo_residual._grafo[v][u]['costo'] = -grafo.atributos(u,v)['costo']
                else:
                    grafo_residual._grafo[v][u]['costo'] = grafo.atributos(v,u)['costo']
            grafo_residual._grafo[v][u]['capacidad'] += bottleneck

            grafo_residual._grafo[u][v]['capacidad'] -= bottleneck
            if grafo_residual._grafo[u][v]['capacidad'] == 0:
                del(grafo_residual._grafo[u][v])

    costo_total = 0
    for u, v, _ in grafo:
        atributos = grafo_residual.atributos(v, u)
        if (atributos):
            flujo = atributos.get('capacidad', 0)
            costo = atributos.get('costo', 0)
            costo_total -= costo * flujo

    return grafo_residual, costo_total
