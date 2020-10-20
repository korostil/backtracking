import copy
import itertools

import networkx as nx

import utils


def step_back(multigraph: nx.MultiGraph, u: int, v: int, key: int, vertex, w_edges: list) -> None:
    """Reverts changes have been done on current step

    Args:
        multigraph: considered multigraph
        u:
        v:
        key:
        vertex:
        w_edges:

    Returns:

    """

    del multigraph.edges[u, v, key]['fixed_z']
    if 'started_node' not in multigraph.nodes[v if u == vertex else u]:
        del multigraph.nodes[v if u == vertex else u]['included_in_z']
    multigraph.graph['length_z'] -= 1

    for u_w, v_w, key_w in w_edges:
        del multigraph.edges[u_w, v_w, key_w]['fixed_w']
        multigraph.graph['length_w'] -= 1
        if tuple(sorted((u_w, v_w))) in multigraph.graph['w']:
            multigraph.graph['w'].remove(tuple(sorted((u_w, v_w))))


@utils.timeout('Simple path for undirected cycles')
def backtracking_1(
        multigraph: nx.MultiGraph, x_edges, y_edges, vertex, timeout: tuple = None, global_timeout: tuple = None
) -> bool:
    """

    Args:
        multigraph:
        x_edges:
        y_edges:
        vertex:
        timeout:
        global_timeout:

    Returns:

    """

    if multigraph.graph['length_z'] == len(x_edges) and multigraph.graph['length_w'] == len(x_edges):
        z = nx.get_edge_attributes(multigraph, 'fixed_z')
        z_edges = set(tuple(sorted(item[:2])) for item in z)
        if z_edges != x_edges and z_edges != y_edges and multigraph.graph['w'] != x_edges and multigraph.graph[
            'w'] != y_edges and \
                utils.is_hamiltonian_cycle(z_edges) and utils.is_hamiltonian_cycle(multigraph.graph['w']):
            return True
        return False

    for u, v, key, attrs in filter(utils.is_non_fixed_edge, multigraph.edges(vertex, data=True, keys=True)):
        if 'included_in_z' in multigraph.nodes[v if u == vertex else u] and multigraph.graph['length_z'] + 1 != len(
                x_edges):
            continue

        multigraph.edges[u, v, key]['fixed_z'] = True
        multigraph.nodes[v if u == vertex else u]['included_in_z'] = True
        multigraph.graph['length_z'] += 1

        added_to_w = []

        for u_w, v_w, key_w, _ in filter(utils.is_non_fixed_edge, multigraph.edges(vertex, data=True, keys=True)):
            multigraph.edges[u_w, v_w, key_w]['fixed_w'] = True
            added_to_w.append((u_w, v_w, key_w))
            multigraph.graph['length_w'] += 1
            multigraph.graph['w'].add(tuple(sorted((u_w, v_w))))

        if added_to_w and utils.has_cycle(multigraph.graph['w']) and (
                multigraph.graph['length_w'] != len(x_edges) or not utils.is_hamiltonian_cycle(multigraph.graph['w'])):
            step_back(multigraph, u, v, key, vertex, added_to_w)
            continue

        if backtracking_1(multigraph, x_edges, y_edges, v, timeout=timeout, global_timeout=global_timeout):
            return True

        step_back(multigraph, u, v, key, vertex, added_to_w)

    return False


def simple_path(graph_x: list, graph_y: list, timeout: int = None, global_timeout: int = None) -> bool:
    """

    Args:
        graph_x:
        graph_y:
        timeout:
        global_timeout:

    Returns:

    """

    x_edges = {tuple(sorted((graph_x[idx - 1], graph_x[idx]))) for idx in range(len(graph_x))}
    y_edges = {tuple(sorted((graph_y[idx - 1], graph_y[idx]))) for idx in range(len(graph_y))}

    multigraph = nx.MultiGraph()
    multigraph.add_edges_from(x_edges)
    multigraph.add_edges_from(y_edges)

    start_node = 1
    start_edges = list(multigraph.edges(start_node))
    for edge_1, edge_2 in itertools.combinations(start_edges, 2):
        if edge_1 == edge_2:
            continue

        edges_w = copy.copy(start_edges)
        list(map(edges_w.remove, [edge_1, edge_2]))

        for u, v in [edge_1, edge_2]:
            multigraph.nodes[u]['included_in_z'], multigraph.nodes[u]['started_node'] = True, True
            multigraph.nodes[v]['included_in_z'], multigraph.nodes[v]['started_node'] = True, True
            multigraph.edges[u, v, 0]['fixed_z'] = True

        for u, v in edges_w:
            try:
                multigraph.edges[u, v, 1]['fixed_w'] = True
            except KeyError:
                multigraph.edges[u, v, 0]['fixed_w'] = True

        multigraph.graph['length_z'] = 2
        multigraph.graph['length_w'] = 2
        multigraph.graph['w'] = set(edges_w)

        if backtracking_1(multigraph, x_edges, y_edges, edge_2[1], timeout=timeout, global_timeout=global_timeout):
            return True

        for u, v in [edge_1, edge_2]:
            if multigraph.nodes[u]:
                del multigraph.nodes[u]['included_in_z']
                del multigraph.nodes[u]['started_node']
            if multigraph.nodes[v]:
                del multigraph.nodes[v]['included_in_z']
                del multigraph.nodes[v]['started_node']
            del multigraph.edges[u, v, 0]['fixed_z']
        for u, v in edges_w:
            try:
                del multigraph.edges[u, v, 1]['fixed_w']
            except KeyError:
                del multigraph.edges[u, v, 0]['fixed_w']

    return False


def get_node_with_min_degree(multigraph: nx.MultiGraph) -> int:
    """

    Args:
        multigraph:

    Returns:

    """

    nodes = {}
    for attr in ('fixed_z', 'fixed_w'):
        for u, v, _ in nx.get_edge_attributes(multigraph, attr):
            if u in nodes:
                nodes[u] += 1
                if nodes[u] == 4:
                    del nodes[u]
            else:
                nodes[u] = 1
            if v in nodes:
                nodes[v] += 1
                if nodes[v] == 4:
                    del nodes[v]
            else:
                nodes[v] = 1

    return max(nodes, key=lambda x: nodes[x]) if nodes else 1


@utils.timeout('Chain edge fixing for undirected cycles')
def backtracking_2(multigraph, x_edges, y_edges, edge, timeout: tuple = None, global_timeout: tuple = None) -> bool:
    """

    Args:
        multigraph:
        x_edges:
        y_edges:
        edge:
        timeout:
        global_timeout:

    Returns:

    """

    fixed_in_z, fixed_in_w = set(), set()

    utils.fix_edge(multigraph, edge, in_z=True, fixed_in_z=fixed_in_z, fixed_in_w=fixed_in_w)

    z = nx.get_edge_attributes(multigraph, 'fixed_z')
    w = nx.get_edge_attributes(multigraph, 'fixed_w')
    if len(z) == len(x_edges) and len(w) == len(x_edges):
        z_edges = set(tuple(sorted(item[:2])) for item in z)
        w_edges = set(tuple(sorted(item[:2])) for item in w)
        if z_edges != x_edges and z_edges != y_edges and w_edges != x_edges and w_edges != y_edges and \
                utils.is_hamiltonian_cycle(z_edges) and utils.is_hamiltonian_cycle(w_edges):
            return True

        for u, v in fixed_in_z:
            del multigraph.edges[u, v, 0]['fixed_z']
        for u, v in fixed_in_w:
            del multigraph.edges[u, v, 0]['fixed_w']
        return False

    if utils.has_cycle(z) or utils.has_cycle(w):
        for u, v in fixed_in_z:
            del multigraph.edges[u, v, 0]['fixed_z']
        for u, v in fixed_in_w:
            del multigraph.edges[u, v, 0]['fixed_w']
        return False

    next_node = get_node_with_min_degree(multigraph)
    for next_edge in filter(
            lambda x: all(
                'fixed_z' not in value and 'fixed_w' not in value
                for key, value in multigraph[x[0]][x[1]].items()
            ),
            multigraph.edges(next_node)
    ):
        if backtracking_2(multigraph, x_edges, y_edges, next_edge, timeout=timeout, global_timeout=global_timeout):
            return True

    for u, v in fixed_in_z:
        del multigraph.edges[u, v, 0]['fixed_z']
    for u, v in fixed_in_w:
        del multigraph.edges[u, v, 0]['fixed_w']

    return False


def chain_edge_fixing(graph_x: list, graph_y: list, timeout: tuple = None, global_timeout: tuple = None) -> bool:
    """

    Args:
        graph_x:
        graph_y:
        timeout:
        global_timeout:

    Returns:

    """

    x, y = nx.Graph(), nx.Graph()
    nx.add_cycle(x, graph_x)
    nx.add_cycle(y, graph_y)

    multigraph = nx.MultiGraph()
    multigraph.add_edges_from(x.edges)
    multigraph.add_edges_from(y.edges)

    utils.fix_multiedges(multigraph)

    x_edges = set(tuple(sorted(item)) for item in x.edges)
    y_edges = set(tuple(sorted(item)) for item in y.edges)

    next_node = get_node_with_min_degree(multigraph)
    for next_edge in filter(
            lambda x: all(
                'fixed_z' not in value and 'fixed_w' not in value
                for key, value in multigraph[x[0]][x[1]].items()
            ),
            multigraph.edges(next_node)
    ):
        if backtracking_2(multigraph, x_edges, y_edges, next_edge, timeout=timeout, global_timeout=global_timeout):
            return True
    return False
