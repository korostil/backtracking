import itertools
import sys
from datetime import datetime, timedelta

import utils


class Vertex:
    """
    name: integer title of the vertex
    incoming_1 and incoming_2: incoming edges
    outgoing_1 and outgoing_2: outgoing edges
    """

    __slots__ = ['name', 'incoming_1', 'incoming_2', 'outgoing_1', 'outgoing_2']

    def __init__(self, name: int):
        self.name = name

        self.incoming_1 = Edge()
        self.incoming_2 = Edge()

        self.outgoing_1 = Edge()
        self.outgoing_2 = Edge()

    def __repr__(self):
        return f'Vertex({self.name})'

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __hash__(self):
        return hash(self.name)


class GraphHasCycle(Exception):
    """"""


class Edge:
    """
    source: vertex from which the edge emanates
    target: vertex which the edge enters
    fixed: True - the edge was fixed in one of the new cycles, False - free to fix
    """

    __slots__ = ['source', 'target', 'fixed']

    def __init__(self, source: Vertex = None, target: Vertex = None, fixed: bool = False):
        self.source = source
        self.target = target
        self.fixed = fixed

    def __repr__(self):
        return f'Edge({self.source.name}, {self.target.name})' if self.source and self.target else 'Edge()'

    def __eq__(self, other):
        return self.source == other.source and self.target == other.target

    def __hash__(self):
        return hash((self.source, self.target))

    def __bool__(self):
        return self.source is not None and self.target is not None


class Graph:
    """"""

    __slots__ = ['edges']

    def __init__(self):
        self.edges = set()

    def __repr__(self):
        return 'Graph([' + ', '.join([f'({edge.source.name}, {edge.target.name})' for edge in self.edges]) + '])'

    def __len__(self):
        return len(self.edges)

    def __iter__(self):
        return self.edges.__iter__()

    def __eq__(self, other):
        return self.edges == other.edges

    def has_cycle(self):
        """Check if the path contains at least one cycle

        Returns:
            bool: True - contains cycles, False - has no cycle
        """

        chain = []
        for item in sorted(self.edges, key=lambda x: (x.source, x.target)):
            if chain and (chain[0] == item.target.name or chain[-1] == item.source.name):
                if chain[0] == item.target.name:
                    chain = [item.source.name, item.target.name] + chain
                else:
                    chain += [item.source.name, item.target.name]
            else:
                chain = [item.source.name, item.target.name]

            if chain[0] == chain[-1]:
                return True

        return False

    def has_vertex(self, vertex: Vertex) -> bool:
        """Checks if the graph has the vertex

        Args:
            vertex: vertex being checked

        Returns:
            bool: True - the graph has vertex, False - otherwise
        """

        return any(edge.target == vertex for edge in self.edges)

    def is_hamiltonian_cycle(self) -> bool:
        """Checks if the graph is a hamiltonian cycle

        Returns:
            bool: True - the graph is a hamiltonian cycle, False - otherwise
        """

        edges = [[item.source.name, item.target.name] for item in self.edges]
        path = edges.pop()
        while True:
            is_ok = False
            idx = -1
            for idx, (ver_1, ver_2) in enumerate(edges):
                if path[-1] == ver_1 and ver_2 not in path:
                    path += [ver_2]
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

    def is_adjacent_with(self, other, start: Vertex, timeout: int = None):
        """

        Args:
            other: Graph that we compare with
            start:
            timeout:

        Returns:

        """

        start_func = datetime.now()
        for incoming_edge, outgoing_edge in itertools.product(
                [start.incoming_1, start.incoming_2], [start.outgoing_1, start.outgoing_2]
        ):
            z, w = Graph(), Graph()
            for edge_z, edge_w in [
                (incoming_edge, utils.get_different_edge({start.incoming_1, start.incoming_2}, incoming_edge)),
                (outgoing_edge, utils.get_different_edge({start.outgoing_1, start.outgoing_2}, outgoing_edge))
            ]:
                z.edges.add(edge_z)
                w.edges.add(edge_w)

            def rec_func(z, w, last_edge: Edge):
                if timeout and datetime.now() - start_func > timedelta(minutes=timeout):
                    return
                vertex = last_edge.target
                rest = utils.get_different_edge({vertex.incoming_1, vertex.incoming_2}, last_edge)
                rest_added = False
                if rest not in w:
                    try:
                        w.edges.add(rest)
                        rest_added = True
                    except GraphHasCycle:
                        return

                for outgoing_edge in [vertex.outgoing_1, vertex.outgoing_2]:
                    if not z.has_vertex(outgoing_edge.target):
                        try:
                            z.edges.add(outgoing_edge)
                        except GraphHasCycle:
                            continue

                        different = utils.get_different_edge({vertex.outgoing_1, vertex.outgoing_2}, outgoing_edge)
                        diff_is_added = False
                        if different not in w:
                            try:
                                w.edges.add(different)
                                diff_is_added = True
                            except GraphHasCycle:
                                z.edges.remove(outgoing_edge)
                                continue

                        if len(z) == len(self):
                            if self != z and other != z and self != w and other != w and z.is_hamiltonian_cycle() \
                                    and w.is_hamiltonian_cycle():
                                return z, w

                            z.edges.remove(outgoing_edge)
                            if diff_is_added:
                                w.edges.remove(different)
                            continue

                        if len(w) == len(self) and (w == self or w == other or not w.is_hamiltonian_cycle()):
                            z.edges.remove(outgoing_edge)
                            if diff_is_added:
                                w.edges.remove(different)
                            continue

                        result = rec_func(z, w, outgoing_edge)
                        if result:
                            return result

                        z.edges.remove(outgoing_edge)
                        if diff_is_added:
                            w.edges.remove(different)

                if rest_added:
                    w.edges.remove(rest)

            result = rec_func(z, w, edge_z)
            if result:
                return True, False

            if timeout and datetime.now() - start_func > timedelta(minutes=timeout):
                return None, True

        return False, False


def fix_edge(z: Graph, w: Graph, edge: Edge, in_z: bool, fixed_in_z: set, fixed_in_w: set):
    """"""

    if in_z:
        target = z
        fixed_in_z.add(edge)
    else:
        target = w
        fixed_in_w.add(edge)

    target.edges.add(edge)
    edge.fixed = True

    i_to_k = ({edge.source.outgoing_1, edge.source.outgoing_2} - {edge}).pop()
    if not i_to_k.fixed:
        fix_edge(z, w, edge=i_to_k, in_z=not in_z, fixed_in_z=fixed_in_z, fixed_in_w=fixed_in_w)

    h_to_j = ({edge.target.incoming_1, edge.target.incoming_2} - {edge}).pop()
    if not h_to_j.fixed:
        fix_edge(z, w, edge=h_to_j, in_z=not in_z, fixed_in_z=fixed_in_z, fixed_in_w=fixed_in_w)


def version_1(graphs: list, timeout: int = None):
    """

    Args:
        graphs:
        timeout:

    Returns:

    """

    success_times, fail_times = [], []
    broken_times = 0

    tests_number = len(graphs)

    for idx, (graph_x, graph_y) in enumerate(graphs):
        start_time = datetime.now()
        if graph_x == graph_y:
            continue

        x, y = Graph(), Graph()
        graph_x, graph_y = list(graph_x), list(graph_y)
        graph = {vertex: Vertex(vertex) for vertex in graph_x}

        for index, vertex in graph.items():
            pos_x, pos_y = graph_x.index(index), graph_y.index(index)

            for graph_target, graph_tuple, pos in [(x, graph_x, pos_x), (y, graph_y, pos_y)]:
                edge = Edge(graph[graph_tuple[pos - 1]], vertex)
                if not vertex.incoming_1:
                    vertex.incoming_1 = edge
                else:
                    vertex.incoming_2 = edge

                if not graph[graph_tuple[pos - 1]].outgoing_1:
                    graph[graph_tuple[pos - 1]].outgoing_1 = edge
                else:
                    graph[graph_tuple[pos - 1]].outgoing_2 = edge

                graph_target.edges.add(edge)

        result, broken = x.is_adjacent_with(y, start=graph[1], timeout=timeout)

        if broken:
            broken_times += 1
        elif result:
            success_times.append((datetime.now() - start_time).seconds)
        else:
            fail_times.append((datetime.now() - start_time).seconds)

        if datetime.now() - start_time > timedelta(minutes=1):
            print(datetime.now(), 'directed cycles:', idx, '/', tests_number, 'passed')

    print(datetime.now(), 'directed cycles: finished')

    adjacent = (sum(success_times) / len(success_times)) if len(success_times) > 0 else 0
    non_adjacent = (sum(fail_times) / len(fail_times)) if len(fail_times) > 0 else 0

    return broken_times, len(success_times), round(adjacent, 2), len(fail_times), round(non_adjacent, 2)


def version_2(graphs: list, timeout: int = None):
    """

    Args:
        graphs: list of 2-tuple x, y graphs
        timeout:

    Returns:

    """

    if not graphs:
        raise Exception('There is no graphs to calculate! Please, check file path or graph generator.')

    tests_number = len(graphs)

    # increase recursion limit
    vertex_number = len(graphs[0][0])
    sys.setrecursionlimit(vertex_number * 10)

    success_times, fail_times = [], []
    broken = 0

    for idx, (graph_x, graph_y) in enumerate(graphs):
        start_time = datetime.now()
        if graph_x == graph_y:
            continue

        x, y = Graph(), Graph()

        graph_x, graph_y = list(graph_x), list(graph_y)
        graph = {vertex: Vertex(vertex) for vertex in graph_x}

        for index, vertex in graph.items():
            pos_x, pos_y = graph_x.index(index), graph_y.index(index)

            for graph_target, graph_tuple, pos in [(x, graph_x, pos_x), (y, graph_y, pos_y)]:
                edge = Edge(graph[graph_tuple[pos - 1]], vertex)
                if not vertex.incoming_1:
                    vertex.incoming_1 = edge
                else:
                    vertex.incoming_2 = edge

                if not graph[graph_tuple[pos - 1]].outgoing_1:
                    graph[graph_tuple[pos - 1]].outgoing_1 = edge
                else:
                    graph[graph_tuple[pos - 1]].outgoing_2 = edge

                graph_target.edges.add(edge)

        z, w = Graph(), Graph()
        for vertex in utils.find_vertices_with_multiedges(graph, True):
            vertex.outgoing_1.fixed = True
            vertex.outgoing_2.fixed = True
            z.edges.add(vertex.outgoing_1)
            w.edges.add(vertex.outgoing_2)

        def backtracking(z: Graph, w: Graph, edge: Edge):
            if timeout and datetime.now() - start_time > timedelta(minutes=timeout):
                return

            fixed_in_z, fixed_in_w = set(), set()
            fix_edge(z, w, edge, in_z=True, fixed_in_z=fixed_in_z, fixed_in_w=fixed_in_w)

            if x != z and y != z and x != w and y != w and z.is_hamiltonian_cycle() and w.is_hamiltonian_cycle():
                return z, w

            if z.has_cycle() or w.has_cycle() or (len(z) == len(x) and len(w) == len(x)):
                for edge_ in fixed_in_w:
                    edge_.fixed = False
                    w.edges.remove(edge_)
                for edge_ in fixed_in_z:
                    edge_.fixed = False
                    z.edges.remove(edge_)
                return

            next_vertex = None
            for vertex in graph.values():
                if not vertex.outgoing_1.fixed and not vertex.outgoing_2.fixed:
                    next_vertex = vertex
                    break

            res = backtracking(z, w, next_vertex.outgoing_1)
            if res:
                return res
            res = backtracking(z, w, next_vertex.outgoing_2)
            if res:
                return res

            for edge in fixed_in_w:
                edge.fixed = False
                w.edges.remove(edge)

            for edge in fixed_in_z:
                edge.fixed = False
                z.edges.remove(edge)

        next_edge = graph[1].outgoing_1
        for edge in z:
            if not edge.target.outgoing_1.fixed and not edge.target.outgoing_2.fixed:
                next_edge = edge.target.outgoing_1
                break

        result = backtracking(z, w, next_edge)

        if timeout and datetime.now() - start_time > timedelta(minutes=timeout):
            broken += 1
        elif result:
            success_times.append((datetime.now() - start_time).seconds)
        else:
            fail_times.append((datetime.now() - start_time).seconds)

        if datetime.now() - start_time > timedelta(minutes=1):
            print(datetime.now(), 'directed cycles 2.0:', idx, '/', tests_number, 'passed')

    print(datetime.now(), 'directed cycles 2.0: finished')

    adjacent = (sum(success_times) / len(success_times)) if len(success_times) > 0 else 0
    non_adjacent = (sum(fail_times) / len(fail_times)) if len(fail_times) > 0 else 0

    return broken, len(success_times), round(adjacent, 2), len(fail_times), round(non_adjacent, 2)
