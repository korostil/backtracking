####Requirements:
python >3.7

`pip install -r requirements.txt`

####Parameters:
`--number` number of vertices

`--path` path to the file with tests

`--times` how many tests to run

`--timeout` runtime threshold for one test (in minutes)

####Examples:
`main.py --number=128 --method=1 --times=100`

`main.py --number=32,40,48 --method=1,3 --times=100`

`main.py --path=<path_to_project>/backtracking/examples/test96.txt`

`main.py --method=3 --path=<path_to_project>/backtracking/examples/test1024.txt`
