from argparse import ArgumentParser
from random import shuffle

from prettytable import PrettyTable

import directed
import undirected
from utils import import_from_file

if __name__ == '__main__':
    funcs = {
        0: {
            'func': directed.version_1,
            'title': 'Backtracking for directed cycles'
        },
        1: {
            'func': undirected.version_1,
            'title': 'Backtracking for undirected cycles'
        },
        2: {
            'func': directed.version_2,
            'title': 'Backtracking 2.0 for directed cycles'
        },
        3: {
            'func': undirected.version_2,
            'title': 'Backtracking 2.0 for undirected cycles'
        }
    }

    parser = ArgumentParser()
    parser.add_argument("--number", dest="n", help="number of vertices")
    parser.add_argument("--path", dest="path", help="path to the file with tests", default=None)
    parser.add_argument("--times", dest="times", help="how many tests to run", default='100')
    parser.add_argument("--timeout", dest="timeout", help="runtime threshold for one test (in minutes)")
    parser.add_argument(
        "--method",
        dest="method",
        help="0 - Backtracking for directed cycles; 1 - Backtracking for undirected cycles; 2 - Backtracking 2.0 for "
             "directed cycles; 3 - Backtracking 2.0 for undirected cycles",
        default='1'
    )

    args = parser.parse_args()

    if args.n:
        print('Number of vertices:', args.n)
    if args.times:
        print('Number of tests:', args.times)
    if args.path:
        print('Test graphs file:', args.path)
    print('Time limit:', (args.timeout + ' minutes') if args.timeout else '(with no limit)')

    methods = list(map(int, args.method.split(',')))
    print('Methods:')
    for method in methods:
        print(' ' * 3, funcs[method]['title'])

    if not args.n and not args.path:
        print('Input error:', 'set parameter "--number" or "--path"! Run "main.py -h" to see the help.')
        exit()
    elif not args.method:
        print('Input error:', 'set parameter "--method"! Run "main.py -h" to see the help.')
        exit()

    if args.path:
        test_graphs = []
        for path in args.path.split(','):
            test_graphs.append(import_from_file(path))
    else:
        test_graphs = []
        for n in list(map(int, args.n.split(','))):
            graphs = []
            vertices = list(range(1, n + 1))
            for _ in range(int(args.times)):
                pair = []
                for _ in range(2):
                    cp = vertices[:]
                    shuffle(cp)
                    pair.append(cp)
                graphs.append(pair)
            test_graphs.append(graphs)

    timeout = int(args.timeout) if args.timeout else None

    table = PrettyTable([
        'Vertex number', 'Method', 'Found', 'Found time (s)', 'Not found', 'Not found time (s)', 'Limit exceeded'
    ])
    for graphs in test_graphs:
        for method in methods:
            limit_exceeded, found, found_time, not_found, not_found_time = funcs[method]['func'](graphs, timeout)
            table.add_row([
                len(graphs[0][0]), funcs[method]['title'], found, found_time, not_found, not_found_time, limit_exceeded
            ])

    print(table)
