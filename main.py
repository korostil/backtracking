import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import sleep

import numpy
from prettytable import PrettyTable

import directed
import exceptions
import undirected
from utils import generate_random_graphs, import_from_file

funcs: dict[int, dict] = {
    0: {'func': directed.simple_path, 'title': 'Simple path for directed cycles'},
    1: {'func': undirected.simple_path, 'title': 'Simple path for undirected cycles'},
    2: {
        'func': directed.chain_edge_fixing,
        'title': 'Chain edge fixing for directed cycles',
    },
    3: {
        'func': undirected.chain_edge_fixing,
        'title': 'Chain edge fixing for undirected cycles',
    },
}


def parse_arguments() -> dict:
    parser = ArgumentParser()
    parser.add_argument("--number", dest="n", help="Number of vertices")
    parser.add_argument("--path", dest="path", help="Path(s) to the file(s) with tests")
    parser.add_argument(
        "--times",
        dest="times",
        help=(
            'How many tests to run '
            '(run that number of tests from "path" argument if it passed)'
        ),
    )
    parser.add_argument(
        "--timeout", dest="timeout", help="Runtime threshold for one test (in minutes)"
    )
    parser.add_argument(
        "--global-timeout",
        dest="global_timeout",
        help="Runtime threshold for all tests (in minutes)",
    )
    parser.add_argument(
        "--method",
        dest="method",
        help=(
            "Method(s) to run. By default runs all methods. "
            "0 - Simple path for directed cycles; "
            "1 - Simple path for undirected cycles; "
            "2 - Chain edge fixing for directed cycles; "
            "3 - Chain edge fixing for undirected cycles"
        ),
        default='0,1,2,3',
    )
    parser.add_argument(
        "--progress",
        dest="progress",
        help="Show intermediate progress (enabled by default)",
        default='true',
    )

    args = parser.parse_args()

    try:
        if not args.n and not args.path:
            raise exceptions.InputError(
                'Set one of required parameter "--number" or "--path"! '
                'Run "main.py -h" to see the help.'
            )
    except exceptions.InputError as e:
        print(e.message)
        exit()
    else:
        arguments = {'methods': list(map(int, args.method.split(',')))}

        for key, value in [
            ('n', args.n.split(',') if args.n else None),
            ('paths', args.path.split(',') if args.path else None),
            ('times', args.times),
            ('timeout', args.timeout),
            ('global_timeout', args.global_timeout),
            ('progress', args.progress),
        ]:
            if value:
                arguments[key] = value

        return arguments


def print_configuration(args: dict) -> None:
    config_table = PrettyTable(['Parameter', 'Value'])
    for row in [
        ['Number of nodes', ', '.join(args['n']) if 'n' in args else '--'],
        ['Number of tests', args['times'] if 'times' in args else '--'],
        [
            'Single test time limit',
            (args['timeout'] + ' minute(s)')
            if 'timeout' in args
            else '(with no limit)',
        ],
        [
            'All tests time limit',
            (args['global_timeout'] + ' minute(s)')
            if 'global_timeout' in args
            else '(with no limit)',
        ],
        ['Methods', '\n'.join(funcs[item]['title'] for item in args['methods'])],
        [
            'Test graphs files',
            '\n'.join(item for item in args['paths'])
            if 'paths' in args
            else '(random graphs)',
        ],
    ]:
        config_table.add_row(row)

    print(config_table)


def handle_result(
    result: bool, start_time: datetime, success_times: list, fail_times: list
) -> None:
    if result:
        success_times.append(
            (datetime.now() - start_time).microseconds
            + (datetime.now() - start_time).seconds * (10**6)
        )
    else:
        fail_times.append(
            (datetime.now() - start_time).microseconds
            + (datetime.now() - start_time).seconds * (10**6)
        )


if __name__ == '__main__':
    configuration = parse_arguments()
    print_configuration(configuration)

    test_graphs = []
    if 'paths' in configuration:
        for path in configuration['paths']:
            graph_pack = import_from_file(path)
            if 'times' in configuration:
                test_graphs.append(graph_pack[: int(configuration['times'])])
            else:
                test_graphs.append(graph_pack)
    else:
        generate_random_graphs(test_graphs, configuration)

    timeout = int(configuration['timeout']) if 'timeout' in configuration else None
    global_timeout = (
        int(configuration['global_timeout'])
        if 'global_timeout' in configuration
        else None
    )
    progress = configuration['progress'] in ('True', 'true', 't')

    table = PrettyTable(
        [
            'Vertex number',
            'Method',
            'Found',
            'Found time (s)',
            'Found SD time (s)',
            'Not found',
            'Not found time (s)',
            'Not found SD time (s)',
            'Limit exceeded',
        ]
    )
    try:
        print()
        print('-' * 30, 'STARTED', '-' * 30)
        print()
        for graphs in test_graphs:
            vertex_number = len(graphs[0][0])

            sys.setrecursionlimit(vertex_number * 10)

            for method in configuration['methods']:
                start_time_method = datetime.now()
                success_times: list = []
                fail_times: list = []
                limit_exceeded = 0

                tests_number = len(graphs)

                for idx, (graph_x, graph_y) in enumerate(graphs, start=1):
                    try:
                        if len(graph_x) != len(graph_y):
                            raise exceptions.InputGraphsLengthError(graph_x, graph_y)

                        if graph_x == graph_y:
                            raise exceptions.EqualInputGraphs(graph_x, graph_y)

                        start_time = datetime.now()

                        kwargs = {}
                        if timeout:
                            kwargs['timeout'] = (start_time, timeout)
                        if global_timeout:
                            kwargs['global_timeout'] = (
                                start_time_method,
                                global_timeout,
                            )

                        result = funcs[method]['func'](graph_x, graph_y, **kwargs)
                        handle_result(result, start_time, success_times, fail_times)

                        if progress:
                            print(
                                datetime.now(),
                                funcs[method]['title'],
                                'on ' + str(len(graph_x)) + ' vertices',
                                idx,
                                '/',
                                tests_number,
                                'passed',
                            )
                    except (
                        exceptions.InputGraphsLengthError,
                        exceptions.EqualInputGraphs,
                    ) as e:
                        print(e.message)
                    except exceptions.SingleTestTimeoutExceeded as e:
                        print(e.message)
                        limit_exceeded += 1
                    except exceptions.AllTestsTimeoutExceeded as e:
                        print(e.message)
                        break
                    except KeyboardInterrupt:
                        print(
                            'The current test has been stopped. '
                            'Press Ctrl+C in 5 seconds to stop process this method.'
                        )
                        try:
                            sleep(5)
                        except KeyboardInterrupt:
                            print('The current method has been stopped')
                            break

                found = len(success_times)
                not_found = len(fail_times)
                found_time = (sum(success_times) / found) if found else 0
                not_found_time = (sum(fail_times) / not_found) if not_found else 0

                table.add_row(
                    [
                        vertex_number,
                        funcs[method]['title'],
                        found,
                        round(found_time / 10**6, 3),
                        round(numpy.std(success_times) / 10**6, 3),
                        not_found,
                        round(not_found_time / 10**6, 3),
                        round(numpy.std(fail_times) / 10**6, 3),
                        limit_exceeded,
                    ]
                )
                print(
                    '-' * 30,
                    vertex_number,
                    str(funcs[method]['title']).upper(),
                    'COMPLETED',
                    '-' * 30,
                )
    except KeyboardInterrupt:
        pass

    print()
    print('-' * 30, 'RESULTS', '-' * 30)
    print()
    print(table)
    print('SD - standard deviation')
