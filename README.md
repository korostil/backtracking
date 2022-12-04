###### Requirements:

python >3.7

`pip install -r requirements.txt`

###### Parameters:

`--mehtod` which method to use:
- `0` - Backtracking for directed cycles; 
- `1` - Backtracking for undirected cycles; 
- `2` - Backtracking 2.0 for directed cycles; 
- `3` - Backtracking 2.0 for undirected cycles

`--number` number of vertices

`--path` path to the file with tests

`--times` how many tests to run

`--timeout` runtime threshold for one test (in minutes)

`--global-timeout` runtime threshold for all tests (in minutes)

`--progress` show(hide) intermediate progress (shown by default)

###### Examples:

`python main.py --number=128 --method=1 --times=100 --progress=false`

`python main.py --number=32,40,48 --method=1,3 --times=100`

`python main.py --path=<path_to_project>/backtracking/examples/test96.txt`

`python main.py --method=3 --path=<path_to_project>/backtracking/examples/test1024.txt`
