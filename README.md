# gap-solver
metaheuristics and mixed integer program (MIP) codes for generalized assignment problem (GAP)
- `gap_wls.py` [Weighting Local Search (WLS)](https://github.com/shunji-umetani/gap-solver/blob/main/gap_wls.py "gap_wls.py")
- `gap_grb.py` [Gurobi implemenation](https://github.com/shunji-umetani/gap-solver/blob/main/gap_grb.py "gap_grb.py") (required Gurobi Optimization)
- `gap_pymip.py` [Python-MIP implementation](https://github.com/shunji-umetani/gap-solver/blob/main/gap_pymip.py "gap_pymip.py") (required Python-MIP library)

## Features
- Simple implementation of metaheuristics in Python.
- Local search with shift and swap neighborhood.
- Adaptive control of penalty weights.

## Usage
```
$ gap_wls.py [-h] [-t TIME] filename 
```
- `filename` GAP instance (mandatory)
- `-t` timelimit (optional, default 60 sec) 
