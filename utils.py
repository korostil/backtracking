import itertools
from collections import Counter
from collections.abc import Iterable, Iterator
from datetime import datetime, timedelta
from random import shuffle
from typing import Any, Callable, Union

import matplotlib.pyplot as plt
import networkx as nx

import exceptions

plt.rcParams["figure.figsize"] = (12, 12)
plt.axis('off')


def get_pyramidal_cycles(number_of_vertices: int, number: int) -> list:
    """Generates list of pyramidal cycles

    Args:
        number_of_vertices: how many vertices in cycle
        number: count of cycles

    Returns:
        list: cycles
    """

    cycles = []

    for _ in range(number):
        cycle_1 = list(range(1, number_of_vertices + 1))
        shuffle(cycle_1)
        cycles.append(
            sorted(itertools.takewhile(lambda x: x < number_of_vertices, cycle_1))
            + sorted(
                itertools.dropwhile(lambda x: x < number_of_vertices, cycle_1),
                reverse=True,
            )
        )

    return cycles


def import_from_file(path: str) -> list:
    """Gets data from the file

    Args:
        path: path to the imported file

    Returns:
        list: list of 2-tuple x, y graphs
    """

    data_set = []

    for pair in open(path).read().split('\n\n'):
        if pair:
            x, y = pair.split('\n')
            data_set.append(
                (tuple(map(int, x.strip().split())), tuple(map(int, y.strip().split())))
            )

    return data_set


def import_from_vns_file(path: str) -> list:
    """Gets data from the file generated by VNS

    Args:
        path: path to the imported file

    Returns:
        list: list of 2-tuple x, y graphs
    """

    data_set = []

    data = open(path).readlines()
    while True:
        try:
            data.pop(0)
            x = (
                data.pop(0)
                .replace('	Initial Cycle 1: ', '')
                .replace(',', ' ')
                .strip()
                .split()
            )
            y = (
                data.pop(0)
                .replace('	Initial Cycle 2: ', '')
                .replace(',', ' ')
                .strip()
                .split()
            )
            data_set.append([tuple(map(int, x)), tuple(map(int, tuple(y)))])
            for _ in range(8):
                data.pop(0)
        except IndexError:
            break

    return data_set


def chunk(it: Iterable, n: int) -> Iterator[tuple[Any, ...]]:
    """Returns chunks of n elements each

    >>> list(chunk(range(10), 3))
    [
        [0, 1, 2, ],
        [3, 4, 5, ],
        [6, 7, 8, ],
        [9, ]
    ]

    >>> list(chunk(list(range(10)), 3))
    [
        [0, 1, 2, ],
        [3, 4, 5, ],
        [6, 7, 8, ],
        [9, ]
    ]
    """

    def _w(g: Iterable) -> Callable[[], tuple[Any, ...]]:
        return lambda: tuple(itertools.islice(g, n))

    return iter(_w(iter(it)), ())


def find_vertices_with_multiedges(graph: dict, graph_type: bool) -> list:
    """Returns all vertices with multiedges

    Args:
        graph: dict of all vertices
        graph_type: True - directed, False - undirected

    Returns:
        list: vertices with multiedges
    """

    result = []
    passed_edges = []

    for vertex in graph.values():
        if graph_type:
            if vertex.outgoing_1 and vertex.outgoing_1 == vertex.outgoing_2:
                result.append(vertex)
        else:
            edges_counter = Counter(vertex.edges)
            for edge in filter(lambda x: edges_counter[x] == 2, edges_counter):
                if edge not in passed_edges:
                    passed_edges.append(edge)
                    result.append((vertex, edge))

    return result


def get_different(items: set, excluded_item: tuple) -> tuple:
    """Gets edge

    Args:
        items: set of items
        excluded_item: edge excluded from that set of items

    Returns:
        Edge:
    """

    different: tuple = ((items - {excluded_item}) if len(items) > 1 else items).pop()
    return different


alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def generate_vertices(number_of_vertices: int) -> list:
    vertices: list = []
    num_liter = 1
    index = 1

    while len(vertices) != number_of_vertices:
        for _ in range(number_of_vertices):
            if index == len(alphabet):
                num_liter += 1
                index = 0
            vertex = alphabet[index : index + num_liter]
            if len(vertex) < num_liter:
                vertex += alphabet[0 : num_liter - len(vertex)]
            vertices.append(vertex)
            index += 1

    return vertices


def vertex_name_converter(name: Union[str, int]) -> str:
    if isinstance(name, int):
        col_str = ''
        while name:
            remainder = name % 26
            if remainder == 0:
                remainder = 26
            col_letter = chr(ord('A') + remainder - 1)
            col_str = col_letter + col_str
            name = int((name - 1) / 26)
        return col_str
    else:
        expn = 0
        col_num = 0
        for char in reversed(name):
            col_num += (ord(char) - ord('A') + 1) * (26**expn)
            expn += 1
        return str(col_num)


def is_non_fixed_edge(edge: tuple) -> bool:
    """Returns an attribute that edge is fixed or not in any of new cycles"""

    return 'fixed_z' not in edge[3] and 'fixed_w' not in edge[3]


def generate_random_graphs(target: list, arguments: dict) -> None:
    """Generate random graphs by number(s) of vertices and
    how many tests to generate for every number

    Args:
        target: list to append pairs of graphs
        arguments: running configuration

    Returns:

    """

    for n in list(map(int, arguments['n'])):
        graphs = []
        vertices = list(range(1, n + 1))
        for _ in range(int(arguments['times']) if 'times' in arguments else 100):
            pair = []
            for _ in range(2):
                cp = vertices[:]
                shuffle(cp)
                pair.append(cp)
            graphs.append(pair)
        target.append(graphs)


def show(G: nx.MultiGraph) -> None:
    pos = nx.circular_layout(G)

    nx.draw_networkx_nodes(G, pos, nodelist=G.nodes, **{"node_size": 500})

    z_edges, w_edges, multiedges, others = [], [], [], []
    for u, v in G.edges():
        if isinstance(G, nx.MultiGraph):
            if 'fixed_z' in G.edges[u, v, 0] and any(
                'fixed_w' in value for key, value in G[u][v].items()
            ):
                multiedges.append((u, v))
            elif 'fixed_z' in G.edges[u, v, 0]:
                z_edges.append((u, v))
            elif any('fixed_w' in value for key, value in G[u][v].items()):
                w_edges.append((u, v))
            else:
                others.append((u, v))
        else:
            if 'fixed_z' in G.edges[u, v] and any(
                'fixed_w' in value for key, value in G[u][v].items()
            ):
                multiedges.append((u, v))
            elif 'fixed_z' in G.edges[u, v]:
                z_edges.append((u, v))
            elif any('fixed_w' in value for key, value in G[u][v].items()):
                w_edges.append((u, v))
            else:
                others.append((u, v))

    nx.draw_networkx_edges(G, pos, edgelist=z_edges, alpha=0.8, edge_color="r", width=2)
    nx.draw_networkx_edges(G, pos, edgelist=w_edges, alpha=0.8, edge_color="b", width=2)
    nx.draw_networkx_edges(
        G, pos, edgelist=multiedges, alpha=0.8, edge_color="#FF00FF", width=2
    )
    nx.draw_networkx_edges(
        G, pos, edgelist=others, alpha=0.8, edge_color="#000000", width=2
    )
    nx.draw_networkx_labels(G, pos, {ver: ver for ver in G.nodes}, font_size=16)

    plt.show()


def has_cycle(edges: Union[set, dict]) -> bool:
    counter: dict = {}

    if isinstance(edges, set):
        for u, v in edges:
            for node in (u, v):
                cnt = counter.get(node, 0)
                if cnt + 1 > 2:
                    return True
                counter[node] = cnt + 1
    else:
        for (u, v, _), _ in edges.items():
            for node in (u, v):
                cnt = counter.get(node, 0)
                if cnt + 1 > 2:
                    return True
                counter[node] = cnt + 1

    return False


def is_hamiltonian_cycle(edges: set[tuple], directed: bool = True) -> bool:
    """Checks if the graph is a hamiltonian cycle

    Returns:
        bool: True - the graph is a hamiltonian cycle, False - otherwise
    """

    graph = nx.Graph(edges)
    try:
        cycle = nx.find_cycle(graph, orientation='original' if directed else 'ignore')
    except nx.NetworkXNoCycle:
        pass
    else:
        if len(cycle) == len(edges):
            return True

    return False


def timeout(method_name: str) -> Callable:
    def decorator_timeout(func):  # type: ignore
        def wrapper(*args, **kwargs):  # type: ignore
            if (
                'timeout' in kwargs
                and kwargs['timeout']
                and datetime.now() - kwargs['timeout'][0]
                > timedelta(minutes=kwargs['timeout'][1])
            ):
                raise exceptions.SingleTestTimeoutExceeded(
                    ' '.join(
                        [
                            str(datetime.now()),
                            method_name + ': single test timeout exceeded!',
                        ]
                    )
                )
            if (
                'global_timeout' in kwargs
                and kwargs['global_timeout']
                and datetime.now() - kwargs['global_timeout'][0]
                > timedelta(minutes=kwargs['global_timeout'][1])
            ):
                raise exceptions.AllTestsTimeoutExceeded(
                    ' '.join(
                        [
                            str(datetime.now()),
                            method_name + ': all tests timeout exceeded!',
                        ]
                    )
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator_timeout


def fix_multiedges(multigraph: nx.MultiGraph) -> None:
    if isinstance(multigraph, nx.MultiDiGraph):
        for node in filter(
            lambda x: len(
                set(multigraph.neighbors(x)) | set(multigraph.predecessors(x))
            )
            < 4,
            multigraph.nodes,
        ):
            edges = list(multigraph.in_edges(node)) + list(multigraph.edges(node))
            for u, v in set(edges):
                if edges.count((u, v)) == 2 and not multigraph.edges[u, v, 0]:
                    multigraph.edges[u, v, 0]['fixed_z'] = True
                    multigraph.edges[u, v, 1]['fixed_w'] = True
    else:
        for node in filter(
            lambda x: len(set(multigraph.neighbors(x))) < 4, multigraph.nodes
        ):
            for u, v in multigraph.edges(node):
                if (
                    multigraph.number_of_edges(u, v) == 2
                    and not multigraph.edges[u, v, 0]
                ):
                    multigraph.edges[u, v, 0]['fixed_z'] = True
                    multigraph.edges[u, v, 1]['fixed_w'] = True


def fix_edge(
    multigraph: nx.MultiGraph, edge: tuple, in_z: bool, fixed_in_z: set, fixed_in_w: set
) -> None:
    u, v = edge
    if in_z:
        fixed_in_z.add(edge)
        multigraph.edges[u, v, 0]['fixed_z'] = True
    else:
        fixed_in_w.add(edge)
        try:
            multigraph.edges[u, v, 1]['fixed_w'] = True
        except KeyError:
            multigraph.edges[u, v, 0]['fixed_w'] = True

    if isinstance(multigraph, nx.MultiDiGraph):
        for next_fixed_edge in [
            get_different(set(multigraph.edges(u)), edge),
            get_different(set(multigraph.in_edges(v)), edge),
        ]:
            fixed = (
                'fixed_z' in multigraph[next_fixed_edge[0]][next_fixed_edge[1]][0]
                or 'fixed_w' in multigraph[next_fixed_edge[0]][next_fixed_edge[1]][0]
            )
            if not fixed:
                fix_edge(
                    multigraph,
                    edge=next_fixed_edge,
                    in_z=not in_z,
                    fixed_in_z=fixed_in_z,
                    fixed_in_w=fixed_in_w,
                )
    else:
        for node in edge:
            fixed_z, fixed_w = 0, 0
            for adj_node, attrs in dict(multigraph[node]).items():
                for _, attrs in attrs.items():
                    if 'fixed_z' in attrs:
                        fixed_z += 1
                    elif 'fixed_w' in attrs:
                        fixed_w += 1

            if fixed_z + fixed_w != 4:
                if fixed_z == 2 or fixed_w == 2:
                    for free_edge in filter(
                        lambda x: all(
                            'fixed_z' not in value and 'fixed_w' not in value
                            for key, value in multigraph[x[0]][x[1]].items()
                        ),
                        multigraph.edges(node),
                    ):
                        fix_edge(
                            multigraph,
                            edge=free_edge,
                            in_z=True if fixed_w == 2 else False,
                            fixed_in_z=fixed_in_z,
                            fixed_in_w=fixed_in_w,
                        )
