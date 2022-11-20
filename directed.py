import itertools
from typing import Optional

import networkx as nx

import utils


def step_back(
    multigraph: nx.MultiDiGraph, u: int, v: int, key: int, w_edges: list
) -> None:
    """Reverts changes have been done on current step"""

    del multigraph.edges[u, v, key]['fixed_z']
    if 'started_node' not in multigraph.nodes[v]:
        del multigraph.nodes[v]['included_in_z']
    multigraph.graph['length_z'] -= 1

    for u_w, v_w, key_w in w_edges:
        del multigraph.edges[u_w, v_w, key_w]['fixed_w']
        multigraph.graph['length_w'] -= 1
        if (u_w, v_w) in multigraph.graph['w']:
            multigraph.graph['w'].remove((u_w, v_w))


@utils.timeout('Simple path for directed cycles')
def backtracking_1(
    multigraph: nx.MultiDiGraph,
    x_edges: set[tuple],
    y_edges: set[tuple],
    vertex: int,
    timeout: Optional[tuple],
    global_timeout: Optional[tuple] = None,
) -> bool:
    for u, v, key, attrs in filter(
        utils.is_non_fixed_edge, multigraph.edges(vertex, data=True, keys=True)
    ):
        # checking for cycle in z
        if 'included_in_z' in multigraph.nodes[v] and multigraph.graph[
            'length_z'
        ] + 1 != len(x_edges):
            continue

        multigraph.edges[u, v, key]['fixed_z'] = True
        multigraph.nodes[v]['included_in_z'] = True
        multigraph.graph['length_z'] += 1

        added_to_w = []
        for source in (
            multigraph.edges(vertex, data=True, keys=True),
            multigraph.in_edges(vertex, data=True, keys=True),
        ):
            for u_w, v_w, key_w, _ in filter(utils.is_non_fixed_edge, source):
                multigraph.edges[u_w, v_w, key_w]['fixed_w'] = True
                added_to_w.append((u_w, v_w, key_w))
                multigraph.graph['length_w'] += 1
                multigraph.graph['w'].add((u_w, v_w))

        if (
            added_to_w
            and utils.has_cycle(multigraph.graph['w'])
            and (
                multigraph.graph['length_w'] != len(x_edges)
                or not utils.is_hamiltonian_cycle(multigraph.graph['w'])
            )
        ):
            step_back(multigraph, u, v, key, added_to_w)
            continue

        if multigraph.graph['length_z'] == len(x_edges) and multigraph.graph[
            'length_w'
        ] == len(x_edges):
            z_edges = {
                item[:2] for item in nx.get_edge_attributes(multigraph, 'fixed_z')
            }
            if (
                z_edges != x_edges
                and z_edges != y_edges
                and multigraph.graph['w'] != x_edges
                and multigraph.graph['w'] != y_edges
                and utils.is_hamiltonian_cycle(z_edges)
                and utils.is_hamiltonian_cycle(multigraph.graph['w'])
            ):
                return True

            step_back(multigraph, u, v, key, added_to_w)
            continue

        if backtracking_1(
            multigraph,
            x_edges,
            y_edges,
            v,
            timeout=timeout,
            global_timeout=global_timeout,
        ):
            return True

        step_back(multigraph, u, v, key, added_to_w)

    return False


def simple_path(
    graph_x: list,
    graph_y: list,
    timeout: Optional[tuple] = None,
    global_timeout: Optional[tuple] = None,
) -> bool:
    x_edges = {(graph_x[idx - 1], graph_x[idx]) for idx in range(len(graph_x))}
    y_edges = {(graph_y[idx - 1], graph_y[idx]) for idx in range(len(graph_y))}

    multigraph = nx.MultiDiGraph()
    multigraph.add_edges_from(x_edges)
    multigraph.add_edges_from(y_edges)

    start_node = 1
    for in_edge, out_edge in itertools.product(
        multigraph.in_edges(start_node), multigraph.edges(start_node)
    ):
        if in_edge == out_edge:
            continue

        for u, v in [in_edge, out_edge]:
            (
                multigraph.nodes[u]['included_in_z'],
                multigraph.nodes[u]['started_node'],
            ) = (True, True)
            (
                multigraph.nodes[v]['included_in_z'],
                multigraph.nodes[v]['started_node'],
            ) = (True, True)
            multigraph.edges[u, v, 0]['fixed_z'] = True

        edges_w = [
            utils.get_different(set(multigraph.in_edges(start_node)), in_edge),
            utils.get_different(set(multigraph.edges(start_node)), out_edge),
        ]
        for u, v in edges_w:
            try:
                multigraph.edges[u, v, 1]['fixed_w'] = True
            except KeyError:
                multigraph.edges[u, v, 0]['fixed_w'] = True

        multigraph.graph['length_z'] = 2
        multigraph.graph['length_w'] = 2
        multigraph.graph['w'] = set(edges_w)

        if backtracking_1(
            multigraph,
            x_edges,
            y_edges,
            out_edge[1],
            timeout=timeout,
            global_timeout=global_timeout,
        ):
            return True

        for u, v in [in_edge, out_edge]:
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


def get_next_edges(multigraph: nx.MultiDiGraph) -> list:
    for node in multigraph.nodes:
        if all(
            'fixed_z' not in value and 'fixed_w' not in value
            for edge in multigraph.edges(node)
            for key, value in multigraph[edge[0]][edge[1]].items()
        ):
            edges: list = multigraph.edges(node)
            return edges
    return []


@utils.timeout('Chain edge fixing for directed cycles')
def backtracking_2(
    multigraph: nx.MultiDiGraph,
    x_edges: set[tuple],
    y_edges: set[tuple],
    edge: tuple,
    timeout: Optional[tuple] = None,
    global_timeout: Optional[tuple] = None,
) -> bool:
    fixed_in_z: set = set()
    fixed_in_w: set = set()

    utils.fix_edge(
        multigraph, edge, in_z=True, fixed_in_z=fixed_in_z, fixed_in_w=fixed_in_w
    )

    z = nx.get_edge_attributes(multigraph, 'fixed_z')
    w = nx.get_edge_attributes(multigraph, 'fixed_w')
    if len(z) == len(x_edges) and len(w) == len(x_edges):
        z_edges = {item[:2] for item in z}
        w_edges = {item[:2] for item in w}
        if (
            z_edges != x_edges
            and z_edges != y_edges
            and w_edges != x_edges
            and w_edges != y_edges
            and utils.is_hamiltonian_cycle(z_edges)
            and utils.is_hamiltonian_cycle(w_edges)
        ):
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

    for next_edge in get_next_edges(multigraph):
        if backtracking_2(
            multigraph,
            x_edges,
            y_edges,
            next_edge,
            timeout=timeout,
            global_timeout=global_timeout,
        ):
            return True

    for u, v in fixed_in_z:
        del multigraph.edges[u, v, 0]['fixed_z']
    for u, v in fixed_in_w:
        del multigraph.edges[u, v, 0]['fixed_w']

    return False


def chain_edge_fixing(
    graph_x: list,
    graph_y: list,
    timeout: Optional[tuple] = None,
    global_timeout: Optional[tuple] = None,
) -> bool:
    x_edges = {(graph_x[idx - 1], graph_x[idx]) for idx in range(len(graph_x))}
    y_edges = {(graph_y[idx - 1], graph_y[idx]) for idx in range(len(graph_y))}

    multigraph = nx.MultiDiGraph()
    multigraph.add_edges_from(x_edges)
    multigraph.add_edges_from(y_edges)

    utils.fix_multiedges(multigraph)

    for next_edge in get_next_edges(multigraph):
        if backtracking_2(
            multigraph,
            x_edges,
            y_edges,
            next_edge,
            timeout=timeout,
            global_timeout=global_timeout,
        ):
            return True
    return False
