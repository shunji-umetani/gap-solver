# gap-solver
metaheuristics and mixed integer program (MIP) codes for generalized assignment problem (GAP)
- `gap_wls.py` [Weighting Local Search (WLS)](https://github.com/shunji-umetani/gap-solver/blob/main/gap_wls.py "gap_wls.py")
- `gap_grb.py` [Gurobi implemenation](https://github.com/shunji-umetani/gap-solver/blob/main/gap_grb.py "gap_grb.py") (required Gurobi Optimization)
- `gap_pymip.py` [Python-MIP implementation](https://github.com/shunji-umetani/gap-solver/blob/main/gap_pymip.py "gap_pymip.py") (required Python-MIP library)

## Feature
- Simple implementation of metaheuristics in Python.
- Local search with shift and swap neighborhood search.
- Adaptive control of penalty weights.
- For GAP instances in http://www.al.cm.is.nagoya-u.ac.jp/~yagiura/gap/.

## Usage
common usage for all codes
```
$ gap_wls.py [-h] [-t TIME] filename 
```
- `filename` GAP instance (mandatory)
- `-t` timelimit (optional, default 60 sec) 

## Author
[Umetani, Shunji](https://github.com/shunji-umetani)

## License
This software is released under the MIT License, see LICENSE.
