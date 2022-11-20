class InputError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class InputGraphsLengthError(Exception):
    def __init__(self, x: list, y: list) -> None:
        self.message = '\n'.join(
            [
                "The number of nodes in X doesn't match the number of nodes in Y!",
                'X: ' + ' '.join(map(str, x)),
                'Y: ' + ' '.join(map(str, y)),
            ]
        )


class EqualInputGraphs(Exception):
    def __init__(self, x: list, y: list) -> None:
        self.message = '\n'.join(
            [
                "Graphs X and Y are the same!",
                'X: ' + ' '.join(map(str, x)),
                'Y: ' + ' '.join(map(str, y)),
            ]
        )


class TimeoutExceeded(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class SingleTestTimeoutExceeded(TimeoutExceeded):
    """"""


class AllTestsTimeoutExceeded(TimeoutExceeded):
    """"""
