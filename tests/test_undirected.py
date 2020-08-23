import pytest

import undirected


@pytest.mark.parametrize('first,second,expected', [(1, 2, False), (1, 1, True)])
def test_vertex_equal(first, second, expected):
    v1 = undirected.Vertex(first)
    v2 = undirected.Vertex(second)

    assert (v1 == v2) is expected


@pytest.mark.parametrize('first,second,expected', [(1, 2, True), (8, 28, True), (7, 3, False)])
def test_vertex_sorting(first, second, expected):
    v1 = undirected.Vertex(first)
    v2 = undirected.Vertex(second)

    assert (v1 < v2) is expected


@pytest.mark.parametrize('first,second,third,expected', [(1, 2, 3, False), (1, 2, 2, True)])
def test_edge_equal(first, second, third, expected):
    v1 = undirected.Vertex(first)
    v2 = undirected.Vertex(second)
    v3 = undirected.Vertex(third)

    assert (undirected.Edge({v1, v2}) == undirected.Edge({v1, v3})) is expected


@pytest.mark.parametrize('first,second,third,expected', [(1, 2, 3, False), (1, 2, 2, True)])
def test_edges_equal(first, second, third, expected):
    graph_1 = undirected.Graph()
    graph_2 = undirected.Graph()
    graph_1.edges.append(undirected.Edge({undirected.Vertex(first), undirected.Vertex(second)}))
    graph_2.edges.append(undirected.Edge({undirected.Vertex(first), undirected.Vertex(third)}))

    assert (graph_1 == graph_2) is expected


@pytest.mark.parametrize('expected', [True, False])
def test_edge_in_edges(expected):
    edge = undirected.Edge({undirected.Vertex(1), undirected.Vertex(2)})
    graph = undirected.Graph()
    if expected:
        graph.edges.append(edge)

    assert (edge in graph) is expected


def test_edge_remove_from_edges():
    edge = undirected.Edge({undirected.Vertex(1), undirected.Vertex(2)})
    graph = undirected.Graph()
    graph.edges.append(edge)
    graph.edges.remove(edge)

    assert edge not in graph


@pytest.mark.parametrize('expected', [False, True])
def test_is_hamiltonian_cycle(expected):
    graph = undirected.Graph()
    graph.edges.append(undirected.Edge({undirected.Vertex(1), undirected.Vertex(2)}))
    graph.edges.append(undirected.Edge({undirected.Vertex(2), undirected.Vertex(3)}))
    if expected:
        graph.edges.append(undirected.Edge({undirected.Vertex(3), undirected.Vertex(1)}))
    else:
        graph.edges.append(undirected.Edge({undirected.Vertex(3), undirected.Vertex(5)}))

    assert graph.is_hamiltonian_cycle() is expected


@pytest.mark.parametrize('version', [1, 2])
@pytest.mark.parametrize(
    'graph_x,graph_y,expected',
    (
            ([5, 4, 11, 14, 2, 8, 9, 10, 15, 3, 7, 13, 1, 12, 16, 6],
             [15, 3, 13, 5, 8, 11, 12, 2, 4, 7, 16, 1, 6, 14, 9, 10],
             True),
            ([1, 9, 7, 4, 12, 11, 5, 16, 13, 6, 3, 2, 8, 14, 15, 10],
             [13, 5, 16, 8, 4, 1, 2, 3, 7, 9, 10, 6, 11, 15, 14, 12],
             True),
            ([10, 16, 2, 7, 1, 3, 8, 4, 11, 13, 5, 12, 14, 6, 9, 15],
             [3, 4, 2, 14, 6, 8, 5, 15, 16, 7, 1, 13, 9, 12, 11, 10],
             True),
            ([14, 7, 1, 12, 9, 5, 6, 3, 11, 15, 10, 4, 8, 2, 13, 16],
             [11, 8, 3, 4, 16, 7, 5, 9, 6, 10, 2, 13, 1, 12, 14, 15],
             True),
            ([4, 11, 7, 3, 6, 13, 1, 16, 2, 12, 9, 5, 10, 15, 8, 14],
             [13, 7, 3, 16, 5, 6, 8, 11, 9, 14, 4, 2, 12, 10, 1, 15],
             True),
            ([5, 10, 7, 1, 14, 16, 4, 3, 2, 9, 6, 8, 11, 13, 15, 12],
             [2, 3, 11, 6, 8, 9, 13, 16, 4, 14, 15, 5, 10, 7, 1, 12],
             True),
            ([9, 6, 8, 14, 12, 13, 3, 4, 10, 1, 16, 2, 7, 5, 15, 11],
             [6, 5, 10, 13, 1, 15, 11, 16, 9, 3, 14, 4, 2, 8, 12, 7],
             True),
            ([6, 13, 9, 3, 12, 14, 8, 7, 16, 2, 1, 4, 11, 10, 15, 5],
             [5, 2, 15, 9, 7, 6, 11, 3, 16, 10, 8, 4, 13, 12, 14, 1],
             True),
            ([7, 1, 11, 8, 12, 15, 6, 3, 16, 4, 13, 9, 5, 10, 14, 2],
             [16, 14, 11, 2, 8, 4, 10, 12, 9, 3, 15, 6, 5, 7, 1, 13],
             True),
            ([9, 11, 1, 6, 5, 4, 16, 7, 13, 10, 12, 3, 14, 15, 8, 2],
             [5, 14, 1, 10, 13, 8, 11, 6, 2, 3, 12, 9, 16, 15, 7, 4],
             True),
            ([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 6, 5], False),
            ([2, 1, 6, 5, 3, 4, 7],
             [1, 2, 3, 7, 4, 5, 6],
             False),
            ([7, 5, 2, 4, 1, 3, 6],
             [7, 1, 5, 3, 6, 4, 2],
             True),
            ([6, 3, 2, 4, 5, 1, 7],
             [7, 4, 5, 2, 1, 6, 3],
             False),
            ([2, 4, 1, 7, 6, 5, 3],
             [7, 1, 6, 5, 2, 3, 4],
             True),
            ([5, 3, 2, 7, 6, 4, 1],
             [7, 1, 3, 6, 4, 5, 2],
             True),
            ([2, 6, 1, 5, 7, 4, 3],
             [3, 7, 4, 5, 6, 2, 1],
             True),
            ([3, 7, 6, 5, 4, 1, 2],
             [5, 6, 2, 1, 3, 7, 4],
             False),
            ([5, 4, 3, 6, 2, 7, 1],
             [4, 6, 5, 7, 2, 1, 3],
             False),
            ([3, 5, 1, 2, 4, 7, 6],
             [5, 7, 3, 2, 6, 1, 4],
             True),
            ([4, 3, 6, 7, 2, 5, 1],
             [3, 5, 1, 6, 2, 7, 4],
             False),
    )
)
def test_final_results(graph_x, graph_y, expected, version):
    if version == 1:
        func = undirected.version_1
    else:
        func = undirected.version_2
    broken, found, _, not_found, _ = func([(graph_x, graph_y)])

    assert broken == 0
    assert bool(found) is expected
    assert bool(not_found) is not expected


@pytest.mark.parametrize(
    'graph,expected',
    [
        ([(1, 2), (2, 1)], True),
        ([(1, 2), (2, 3)], False),
        ([(1, 2), (2, 3), (3, 4), (10, 11), (11, 10)], True),
        ([(1, 2), (2, 3), (3, 4), (4, 1)], True),
        ([(1, 2), (13, 18), (10, 22), (21, 17), (4, 3), (9, 13), (16, 19), (22, 11), (5, 14), (14, 6), (7, 12), (3, 20),
          (19, 9), (17, 23), (23, 10), (2, 15), (20, 16), (11, 1), (12, 21)], False),
        ([(9, 27), (2, 19), (9, 18), (27, 33), (19, 29), (2, 18), (31, 33), (4, 29), (13, 31), (15, 23), (23, 28),
          (28, 36), (13, 24), (10, 25), (3, 10), (1, 3), (25, 36), (11, 32), (4, 32), (8, 36), (8, 20), (12, 36),
          (11, 21), (5, 21), (1, 15), (5, 22), (20, 35), (14, 30), (17, 30), (26, 34), (16, 34), (7, 35), (6, 22)],
         True),
        ([(1, 2), (2, 3), (2, 4), (3, 5), (4, 6), (6, 7), (7, 8), (8, 1)], True),
        ([(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)], True),
        ([(1, 2), (2, 3), (3, 4), (4, 5), (3, 6), (3, 8), (8, 7), (9, 11), (9, 10), (9, 3)], False),
        ([(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)], True),
        ([], False),
        ([(1, 3), (1, 15), (2, 18), (2, 19), (3, 10), (4, 29), (4, 32), (5, 21), (5, 22), (6, 22), (7, 35), (8, 20),
          (8, 36), (9, 18), (9, 27), (10, 25), (11, 21), (11, 32), (12, 36), (13, 24), (13, 31), (14, 30), (15, 23),
          (16, 34), (17, 30), (19, 29), (20, 35), (23, 28), (25, 36), (26, 34), (27, 33), (28, 36), (31, 33)], True),
    ]
)
def test_cycle_checker(graph: list, expected):
    vertices = {}
    graph_for_check = undirected.Graph()
    for left, right in graph:
        if left not in vertices:
            ver_1 = undirected.Vertex(left)
            vertices[left] = ver_1
        else:
            ver_1 = vertices[left]

        if right not in vertices:
            ver_2 = undirected.Vertex(right)
            vertices[right] = ver_2
        else:
            ver_2 = vertices[right]

        edge = undirected.Edge({ver_1, ver_2})
        ver_1.edges.edges.append(edge)
        ver_2.edges.edges.append(edge)
        graph_for_check.edges.append(edge)

    assert graph_for_check.has_cycle() is expected


@pytest.mark.parametrize(
    'graph,expected',
    [
        ([(1, 2), (2, 3)], 1),
        ([(1, 5), (5, 2), (2, 3), (3, 4), (4, 5), (5, 6)], 1),
        ([(1, 3), (2, 3), (3, 4), (3, 5)], 1),
    ]
)
def test_min_degree_vertex(graph, expected):
    vertices = {}

    for left, right in graph:
        if left not in vertices:
            ver_1 = undirected.Vertex(left)
            vertices[left] = ver_1
        else:
            ver_1 = vertices[left]

        if right not in vertices:
            ver_2 = undirected.Vertex(right)
            vertices[right] = ver_2
        else:
            ver_2 = vertices[right]

        edge = undirected.Edge({ver_1, ver_2})
        ver_1.edges.edges.append(edge)
        ver_2.edges.edges.append(edge)

    assert undirected.get_vertex_with_min_degree(vertices.values()) == vertices[expected]
