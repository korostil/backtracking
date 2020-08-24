import itertools
import sys
from collections import Counter
from datetime import datetime, timedelta

import utils


class Vertex:
    """"""

    __slots__ = ['name', 'edges']

    def __init__(self, name: int):
        self.name = name
        self.edges = Graph()

    def __repr__(self):
        return 'Vertex(' + str(self.name) + ')'

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __hash__(self):
        return hash(self.name)

    def count_fixed_edges(self):
        return sum(1 for _ in self.edges if _.fixed_z or _.fixed_w)


class Edge:
    """"""

    __slots__ = ['vertices', 'name', 'fixed_z', 'fixed_w']

    def __init__(self, vertices: set, fixed_z: bool = False, fixed_w: bool = False):
        self.vertices = vertices
        self.name = ', '.join(str(vertex.name) for vertex in sorted(self.vertices))
        self.fixed_z = fixed_z
        self.fixed_w = fixed_w

    def __repr__(self):
        return f'Edge({self.name})'

    def __eq__(self, other):
        return self.vertices == other.vertices

    def __hash__(self):
        return hash(self.name)


class Graph:
    """"""

    __slots__ = ['edges']

    def __init__(self, edges: list = None):
        self.edges = edges or []

    def __repr__(self):
        edges = sorted(tuple(vertex.name for vertex in sorted(edge.vertices)) for edge in self.edges)
        return 'Graph([' + ' | '.join(map(str, edges)) + '])'

    def __getitem__(self, item):
        return self.edges[item]

    def __len__(self):
        return len(self.edges)

    def __eq__(self, other):
        return set(self.edges) == set(other.edges)

    def __sub__(self, other):
        return Graph(list(set(self.edges) - set(other.edges)))

    def __rsub__(self, other):
        return Graph(list(set(self.edges) - set(other.edges)))

    def has_cycle(self):
        """"""

        edges = set(self.edges)

        if len(edges) != len(self.edges):
            return True

        def dfs(vertex: Vertex, passed_vertices: set, passed_edges: Graph):
            for next_edge in edges & set(vertex.edges - passed_edges):
                next_vertex = (next_edge.vertices - {vertex}).pop()

                if next_vertex in passed_vertices:
                    return True

                passed_vertices.add(next_vertex)
                passed_edges.edges.append(next_edge)
                edges.remove(next_edge)

                res = dfs(next_vertex, passed_vertices, passed_edges)
                if res:
                    return True

        while edges:
            edge = edges.pop()
            for start_vertex in edge.vertices:
                if dfs(start_vertex, set(edge.vertices), Graph([edge])):
                    return True

        return False

    def is_hamiltonian_cycle(self):
        """"""

        edges = [sorted([vertex.name for vertex in item.vertices]) for item in self.edges]
        path = edges.pop()
        while True:
            is_ok = False
            idx = -1
            for idx, (ver_1, ver_2) in enumerate(edges):
                if path[-1] == ver_1 and ver_2 not in path:
                    path += [ver_2]
                    is_ok = True
                    break
                elif path[-1] == ver_2 and ver_1 not in path:
                    path += [ver_1]
                    is_ok = True
                    break
                elif path[0] == ver_1 and ver_2 not in path:
                    path = [ver_2] + path
                    is_ok = True
                    break
                elif path[0] == ver_2 and ver_1 not in path:
                    path = [ver_1] + path
                    is_ok = True
                    break

            if len(path) == len(self.edges) and len(edges) == 1 and {path[0], path[-1]} == set(edges[0]):
                return True

            if not is_ok:
                return False
            else:
                edges.pop(idx)

    def is_adjacent_with(self, other, start, timeout: int = None):
        """"""

        start_func = datetime.now()
        for to_z in itertools.combinations(start.edges, 2):
            z, w = Graph(), Graph()

            next_vertex = None
            to_w = start.edges[:]
            for item in to_z:
                to_w.remove(item)
            for item_z, item_w in zip(to_z, to_w):
                if not next_vertex:
                    next_vertex = set(item_z.vertices) - {start}
                z.edges.append(item_z)
                w.edges.append(item_w)

            def rec_func(z, w, vertex):
                if timeout and datetime.now() - start_func > timedelta(minutes=timeout):
                    return

                if len(z) == len(self) and len(w) == len(self):
                    if self == z or other == z or self == w or other == w or \
                            not z.is_hamiltonian_cycle() or not w.is_hamiltonian_cycle():
                        return None
                    return z, w

                doubles = Counter(vertex.edges)
                possible_way_z = vertex.edges - z - w
                doubles = set(filter(lambda x: doubles[x] > 1, doubles))
                for edge_to_z in possible_way_z:
                    next_vertex = (edge_to_z.vertices - {vertex}).pop()
                    z.edges.append(edge_to_z)
                    edges_to_w = []
                    if len(w) != len(self):
                        has_cycle = False
                        possible_way_w = set(possible_way_z) - {edge_to_z}
                        possible_way_w.update(doubles)
                        for edge_to_w in possible_way_w:
                            if edge_to_w not in w:
                                w.edges.append(edge_to_w)
                                edges_to_w.append(edge_to_w)
                                if w.has_cycle() and len(w) != len(self):
                                    has_cycle = True
                                    break

                        if has_cycle:
                            z.edges.remove(edge_to_z)
                            for item in edges_to_w:
                                w.edges.remove(item)
                            continue

                    result = rec_func(z, w, next_vertex)
                    if result:
                        return result
                    z.edges.remove(edge_to_z)
                    for item in edges_to_w:
                        w.edges.remove(item)

            result = rec_func(z, w, next_vertex.pop())
            if result:
                return True

            if timeout and datetime.now() - start_func > timedelta(minutes=timeout):
                return None

        return False


def fix_edge(z: Graph, w: Graph, edge: Edge, in_z: bool, fixed_in_z: list, fixed_in_w: list):
    """"""

    if in_z and edge in w or not in_z and edge in z:
        return

    if in_z:
        target = z
        fixed_in_z.append(edge)
        edge.fixed_z = True
        attr = 'fixed_z'
    else:
        target = w
        fixed_in_w.append(edge)
        edge.fixed_w = True
        attr = 'fixed_w'

    target.edges.append(edge)

    vertices = list(edge.vertices)

    for vertex_idx in range(2):
        if sum(1 for edge_ in vertices[vertex_idx].edges if getattr(edge_, attr)) == 2:
            for free_edge in vertices[vertex_idx].edges:
                if not free_edge.fixed_z and not free_edge.fixed_w:
                    fix_edge(z, w, edge=free_edge, in_z=not in_z, fixed_in_z=fixed_in_z, fixed_in_w=fixed_in_w)


def get_vertex_with_min_degree(graph) -> Vertex:
    """Return vertex with minimum degree in the graph

    Args:
        graph:

    Returns:
        Vertex: vertex with minimum degree
    """

    try:
        return min(filter(lambda x: x.count_fixed_edges() != 4, graph), key=lambda x: 4 - x.count_fixed_edges())
    except ValueError:
        pass


def version_1(graphs, timeout: int = None):
    if not graphs:
        raise Exception('There is no graphs to calculate! Please, check file path or graph generator.')

    success_times, fail_times = [], []
    broken = 0

    tests_number = len(graphs)

    for idx, (graph_x, graph_y) in enumerate(graphs, start=1):
        start_time = datetime.now()

        x, y = Graph(), Graph()
        graph = {vertex: Vertex(vertex) for vertex in graph_x}

        for index, vertex in graph.items():
            pos_x, pos_y = graph_x.index(index), graph_y.index(index)

            for graph_target, graph_tuple, pos in [(x, graph_x, pos_x), (y, graph_y, pos_y)]:
                edge = Edge({graph[graph_tuple[pos - 1]], vertex})
                vertex.edges.edges.append(edge)
                graph_target.edges.append(edge)

                try:
                    edge = Edge({vertex, graph[graph_tuple[pos + 1]]})
                except IndexError:
                    edge = Edge({vertex, graph[graph_tuple[0]]})
                vertex.edges.edges.append(edge)

        result = x.is_adjacent_with(y, start=graph[1], timeout=timeout)
        if timeout and datetime.now() - start_time > timedelta(minutes=timeout):
            broken += 1
        elif result:
            success_times.append((datetime.now() - start_time).seconds)
        else:
            fail_times.append((datetime.now() - start_time).seconds)

        if datetime.now() - start_time > timedelta(minutes=1):
            print(datetime.now(), 'undirected cycles:', idx, '/', tests_number, 'passed')

    print(datetime.now(), 'undirected cycles: finished')

    adjacent = (sum(success_times) / len(success_times)) if len(success_times) > 0 else 0
    non_adjacent = (sum(fail_times) / len(fail_times)) if len(fail_times) > 0 else 0

    return broken, len(success_times), round(adjacent, 2), len(fail_times), round(non_adjacent, 2)


def version_2(graphs, timeout: int = None):
    """"""

    if not graphs:
        raise Exception('There is no graphs to calculate! Please, check file path or graph generator.')

    # increase recursion limit
    vertex_number = len(graphs[0][0])
    sys.setrecursionlimit(vertex_number * 10)

    success_times, fail_times = [], []
    broken = 0

    tests_number = len(graphs)

    for idx, (graph_x, graph_y) in enumerate(graphs, start=1):
        start_time = datetime.now()
        x, y = Graph(), Graph()
        graph_x, graph_y = list(graph_x), list(graph_y)
        graph = {vertex: Vertex(vertex) for vertex in graph_x}

        for index, vertex in graph.items():
            pos_x, pos_y = graph_x.index(index), graph_y.index(index)

            for graph_target, graph_tuple, pos in [(x, graph_x, pos_x), (y, graph_y, pos_y)]:
                edge = Edge({graph[graph_tuple[pos - 1]], vertex})
                vertex.edges.edges.append(edge)
                graph[graph_tuple[pos - 1]].edges.edges.append(edge)
                graph_target.edges.append(edge)

        z, w = Graph(), Graph()
        for vertex, max_edge in utils.find_vertices_with_multiedges(graph, False):
            for edge in vertex.edges:
                if edge == max_edge:
                    if edge not in z:
                        edge.fixed_z = True
                        z.edges.append(edge)
                    else:
                        edge.fixed_w = True
                        w.edges.append(edge)

        def backtracking(z: Graph, w: Graph, edge: Edge):
            if timeout and datetime.now() - start_time > timedelta(minutes=timeout):
                return

            fixed_in_z, fixed_in_w = [], []

            fix_edge(z, w, edge, in_z=True, fixed_in_z=fixed_in_z, fixed_in_w=fixed_in_w)

            if x != z and y != z and x != w and y != w and z.is_hamiltonian_cycle() and w.is_hamiltonian_cycle():
                return z, w

            if z.has_cycle() or w.has_cycle() or (len(z) == len(x) and len(w) == len(x)):
                for edge_ in fixed_in_w:
                    edge_.fixed_w = False
                    w.edges.remove(edge_)
                for edge_ in fixed_in_z:
                    edge_.fixed_z = False
                    z.edges.remove(edge_)
                return

            next_vertex = get_vertex_with_min_degree(graph.values())
            for edge in [_ for _ in next_vertex.edges if not _.fixed_z and not _.fixed_w]:
                res = backtracking(z, w, edge)
                if res:
                    return res

            for edge_ in fixed_in_w:
                edge_.fixed_w = False
                w.edges.remove(edge_)
            for edge_ in fixed_in_z:
                edge_.fixed_z = False
                z.edges.remove(edge_)

        next_vertex = get_vertex_with_min_degree(graph.values())
        next_edge = [_ for _ in next_vertex.edges if not _.fixed_w and not _.fixed_z][0]
        result = backtracking(z, w, next_edge)

        if timeout and datetime.now() - start_time > timedelta(minutes=timeout):
            broken += 1
        elif result:
            success_times.append((datetime.now() - start_time).seconds)
        else:
            fail_times.append((datetime.now() - start_time).seconds)

        if datetime.now() - start_time > timedelta(minutes=1):
            print(datetime.now(), 'undirected cycles 2.0:', idx, '/', tests_number, 'passed')

    print(datetime.now(), 'undirected cycles 2.0: finished')

    adjacent = (sum(success_times) / len(success_times)) if len(success_times) > 0 else 0
    non_adjacent = (sum(fail_times) / len(fail_times)) if len(fail_times) > 0 else 0

    return broken, len(success_times), round(adjacent, 2), len(fail_times), round(non_adjacent, 2)
