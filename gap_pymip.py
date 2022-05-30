#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
#   Python-MIP code for generalized assignment problem (GAP)
#
#   Author: Umetani, Shunji <umetani@ist.osaka-u.ac.jp>
#   Date: 2022/05/30
# --------------------------------------------------------------------

# import modules -----------------------------------------------------
import sys
import time
import argparse
from mip import *

# constant -----------------------------------------------------------
TIME_LIMIT = 60.0  # default time limit for solver

# class --------------------------------------------------------------

# --------------------------------------------------------------------
#   GAP data
# --------------------------------------------------------------------
class Gap:
    def __init__(self):
        self.num_agent = 0  # number of agents
        self.num_job = 0  # number of jobs
        self.cost = []  # c[i,j]: cost for assignment of job j to agent i
        self.res = []  # a[i,j]: resource consumption for assignment of job j to agenet i
        self.cap = []  # b[i]: resource capacity of agent i

    # read GAP data --------------------------------------------------
    def read(self, args):
        # open file and read data
        input_file = open(args.filename, 'r')
        data = input_file.read()
        input_file.close()
        data = data.split()
        # initialize GAP data
        self.num_agent = int(data[0])  # number of agents
        self.num_job = int(data[1])  # number of jobs
        self.cost = [[0 for j in range(self.num_job)] for i in range(self.num_agent)]
        self.res = [[0 for j in range(self.num_job)] for i in range(self.num_agent)]
        self.cap = [0 for i in range(self.num_agent)]
        cnt = 2
        # read cost
        for i in range(self.num_agent):
            for j in range(self.num_job):
                (self.cost)[i][j] = int(data[cnt])
                cnt +=1
        # read resource consumption
        for i in range(self.num_agent):
            for j in range(self.num_job):
                (self.res)[i][j] = int(data[cnt])
                cnt +=1
        # read resource capacity
        for i in range(self.num_agent):
            (self.cap)[i] = int(data[cnt])
            cnt +=1

    # write GAP data --------------------------------------------------
    def write(self):
        print('#agents:\t{}'.format(self.num_agent))
        print('#jobs:\t\t{}'.format(self.num_job))
        print('cost:\t{}'.format(self.cost))
        print('resource:\t{}'.format(self.res))
        print('capacity:\t{}'.format(self.cap))


# --------------------------------------------------------------------
#   solve MIP model
#
#   gap(I): GAP data
#   sol(I/O): job assignment to agent
#   args(I): arguments
# --------------------------------------------------------------------
def solve_mip(gap, sol, args):
    print('\n[solve MIP model]')

    # generate model
    mip_model = Model()

    # variables
    x = {}
    for i in range(gap.num_agent):
        for j in range(gap.num_job):
            x[i,j] = mip_model.add_var(var_type=BINARY, name='x({},{})'.format(i,j))

    # objective function
    mip_model.objective = minimize(xsum((gap.cost)[i][j] * x[i,j] for i,j in x))

    # constraints
    for i in range(gap.num_agent):
        mip_model.add_constr(xsum((gap.res)[i][j] * x[i,j] for j in range(gap.num_job)) <= (gap.cap)[i])
    for j in range(gap.num_job):
        mip_model.add_constr(xsum(x[i,j] for i in range(gap.num_agent)) == 1)

    # write LP file
    #fn_base, fn_ext = os.path.splitext(os.path.basename(args.filename))  # filename and extension
    #cpxlp_fn = '{}.lp'.format(fn_base)
    #mip_model.write(cpxlp_fn)

    # solve MIP model
    mip_model.max_mip_gap = 0.0  # set relative tolerance for checking optimality
    mip_model.max_mip_gap_abs = 0.0  # set absolute tolerance for checking optimality
    mip_model.max_seconds=args.time  # time limit for computation
    mip_model.threads = 1  # number of threads
    mip_model.optimize()

    # get solutions
    if mip_model.num_solutions:
        for i,j in x:
            if x[i,j].x > 0.5:
                sol[j] = i
    print(sol)


# --------------------------------------------------------------------
#   parse arguments
# --------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser('GAP')
    # instance filename
    parser.add_argument('filename', action='store')
    # timelimit for solver
    parser.add_argument('-t', '--time', help='time limit for weighting local search', type=float, default=TIME_LIMIT)
    return parser.parse_args()

# --------------------------------------------------------------------
#   main
# --------------------------------------------------------------------
def main(argv=sys.argv):
    # parse arguments
    args = parse_args()

    # set starting time
    start_time = time.time()

    # read instance
    gap = Gap()
    gap.read(args)
    gap.write()

    # solve GAP
    sol = [None for _ in range(gap.num_job)]
    solve_mip(gap,sol,args)

    # set completion time
    end_time = time.time()

    # display computation time
    print('\nTotal time:\t%.3f sec' % (end_time - start_time))

# main ---------------------------------------------------------------
if __name__ == "__main__":
    main()

# --------------------------------------------------------------------
#   end of file
# --------------------------------------------------------------------
