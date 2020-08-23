import pytest

import directed
import utils


def test_import():
    graph_set = utils.import_from_file('../examples/test32.txt')
    check = (
        (
            9, 3, 10, 8, 29, 19, 30, 20, 1, 25, 27, 21, 16, 15, 12, 32, 6, 22, 7, 24, 17, 28, 4, 23, 18, 11, 14, 2, 5,
            26, 31, 13
        ),
        (
            4, 3, 28, 14, 6, 12, 29, 7, 24, 5, 21, 26, 23, 15, 32, 2, 13, 8, 10, 27, 9, 11, 18, 16, 19, 22, 25, 30, 17,
            31, 20, 1
        )
    )
    assert (check in graph_set) is True


def test_pyramidal_cycles():
    utils.get_pyramidal_cycles(7, 2)


def test_import_vns():
    graph_set = utils.import_from_vns_file('../examples/pyramidal64.txt')
    check = [
        (
            1, 2, 3, 4, 5, 7, 8, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 32, 33, 34, 35,
            36, 38, 40, 41, 42, 43, 45, 46, 47, 49, 50, 51, 52, 53, 55, 57, 60, 61, 64, 63, 62, 59, 58, 56, 54, 48,
            44, 39, 37, 31, 25, 17, 11, 10, 9, 6
        ),
        (
            1, 2, 4, 5, 6, 7, 8, 10, 12, 13, 14, 16, 17, 18, 19, 20, 21, 23, 24, 25, 27, 28, 31, 32, 33, 35, 36, 37,
            38, 39, 41, 44, 46, 47, 48, 49, 51, 52, 54, 55, 58, 59, 60, 63, 64, 62, 61, 57, 56, 53, 50, 45, 43, 42, 40,
            34, 30, 29, 26, 22, 15, 11, 9, 3
        )
    ]
    assert (check in graph_set) is True


@pytest.mark.parametrize(
    'graph,expected',
    [
        ([(1, 2), (1, 2)], [1]),
        ([(1, 2), (1, 4), (2, 3), (2, 3), (3, 4), (3, 5), (4, 2), (4, 5), (5, 6), (5, 6), (6, 1), (6, 1)], [2, 5, 6]),
        ([(1, 2), (1, 2), (2, 3), (2, 3), (3, 1), (3, 1)], [1, 2, 3]),
    ]
)
def test_finding_vertices_with_multiedges_directed(graph, expected):
    vertices = {}
    graph_for_check = directed.Graph()
    for left, right in graph:
        if left not in vertices:
            ver_1 = directed.Vertex(left)
            vertices[left] = ver_1
        else:
            ver_1 = vertices[left]

        if right not in vertices:
            ver_2 = directed.Vertex(right)
            vertices[right] = ver_2
        else:
            ver_2 = vertices[right]

        edge = directed.Edge(ver_1, ver_2)
        if not ver_1.outgoing_1:
            ver_1.outgoing_1 = edge
        else:
            ver_1.outgoing_2 = edge
        if not ver_1.incoming_1:
            ver_2.incoming_1 = edge
        else:
            ver_2.incoming_2 = edge
        graph_for_check.edges.add(edge)

    assert utils.find_vertices_with_multiedges(vertices, True) == [vertices[item] for item in expected]


def test_get_different():
    graph = directed.Graph()
    edge_1 = directed.Edge(directed.Vertex(1), directed.Vertex(2))
    edge_2 = directed.Edge(directed.Vertex(1), directed.Vertex(3))
    graph.edges.add(edge_1)
    graph.edges.add(edge_2)

    assert utils.get_different_edge({edge_1, edge_2}, edge_1) == edge_2
    assert utils.get_different_edge({edge_1, edge_2}, edge_2) == edge_1
