#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
#   weighting local search for GAP
#
#   Author: Umetani, Shunji <umetani@ist.osaka-u.ac.jp>
#   Date: 2022/05/18
# --------------------------------------------------------------------

# import modules -----------------------------------------------------
import sys
import time
import random
import argparse
import copy

# constant -----------------------------------------------------------
TIME_LIMIT = 60  # default time limit for iterated local search
INTVL_TIME = 1.0  # interval time for display logs
RANDOM_SEED = 0  # default random seed
NUM_EPSILON = 0.001  # tolerance for numerical error
INC_WT_RATIO = 0.2  # ratio of increasing penalty weight
DEC_WT_RATIO = 0.1  # ratio of decreasing penalty weight

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
            cnt += 1

    # write GAP data --------------------------------------------------
    def write(self):
        print('#agents:\t{}'.format(self.num_agent))
        print('#jobs:\t\t{}'.format(self.num_job))
        print('cost:\t{}'.format(self.cost))
        print('resource:\t{}'.format(self.res))
        print('capacity:\t{}'.format(self.cap))


# --------------------------------------------------------------------
#   working data
# --------------------------------------------------------------------
class Work:
    def __init__(self,gap):
        self.sol = [None for _ in range(gap.num_job)]  # job assignment to agent
        self.wt = [1.0 for _ in range(gap.num_agent)]  # penalty weight for capacity constraint
        self.obj = 0.0  # objective value
        self.used = [0 for _ in range(gap.num_agent)]  # used resource for agent
        self.plt = 0.0  # weighted penalty
        self.job = [set() for _ in range(gap.num_agent)]  # set of jobs assigned to each agent

    # copy -----------------------------------------------------------
    def copy(self,org):
        self.sol = org.sol[:]
        self.wt = org.wt[:]
        self.obj = org.obj
        self.used = org.used[:]
        self.plt = org.plt
        self.job = copy.deepcopy(org.job)

    # calculate objective value --------------------------------------
    def calc_obj(self,gap):
        self.obj = 0.0
        for j in range(gap.num_job):
            i = (self.sol)[j]
            self.obj += (gap.cost)[i][j]

    # calculate used resource ----------------------------------------
    def calc_used(self,gap):
        for i in range(gap.num_agent):
            (self.used)[i] = 0
        for j in range(gap.num_job):
            i = (self.sol)[j]
            (self.used)[i] += (gap.res)[i][j]

    # calculate weighted penalty -------------------------------------
    def calc_plt(self,gap):
        self.plt = 0.0
        for i in range(gap.num_agent):
            self.plt += (self.wt)[i] * max(0, (self.used)[i] - (gap.cap)[i])

    # calculate set of jobs assigned to each agent -------------------
    def calc_job(self,gap):
        for i in range(gap.num_agent):
            (self.job)[i].clear()
        for j in range(gap.num_job):
            i = (self.sol)[j]
            (self.job)[i].add(j)

    # average penalty weight -----------------------------------------
    def avg_wt(self,gap):
        avg = 0.0
        for i in range(gap.num_agent):
            avg += (self.wt)[i]
        return avg / float(gap.num_agent)

    # write working data ---------------------------------------------
    def write(self,gap):
        # check violated capacity constraint
        vio = set()
        for i in range(gap.num_agent):
            if (self.used)[i]-(gap.cap)[i] > 0:
                vio.add(i)
        print('\n[GAP solution]')
        print('sol= {}'.format(self.sol))
        if vio:
            print('vio= {}'.format(vio))
        print('obj= {}'.format(self.obj))
        #print('plt= {:g}'.format(self.plt))


# function -----------------------------------------------------------

# --------------------------------------------------------------------
#   initialize solution
#
#   gap(I): GAP data
#   work(I/O): working data
# --------------------------------------------------------------------
def init_sol(gap,work):
    # random assignment
    for j in range(gap.num_job):
        (work.sol)[j] = random.randrange(0,gap.num_agent)

    # initialize obj, used, plt, job
    work.calc_obj(gap)
    work.calc_used(gap)
    work.calc_plt(gap)
    work.calc_job(gap)

# --------------------------------------------------------------------
#   weighting local search
#
#   gap(I): GAP data
#   work(I/O): working data
#   time_limit(I): time_limit
# --------------------------------------------------------------------
def weight_local_search(gap,work,time_limit):
    print('\n[weighting local search]')
    # generate initial solution
    init_sol(gap,work)

    # initialize current working data
    cur_work = Work(gap)
    cur_work.copy(work)

    # initialize penalty weight
    init_weight(gap, cur_work)

    # weighting local search
    start_time = cur_time = disp_time = time.time()
    cnt = 0
    while cur_time - start_time < time_limit:
        best_obj = work.obj
        # local search algorithm
        local_search(gap,work,cur_work)
        # update penalty weight
        update_weight(gap,cur_work,work.obj)
        #print()
        cur_time = time.time()
        cnt += 1
        # display current status
        if work.obj < best_obj:
            print('{}\t{:g} ({:g})\t*{:g}\t{:g}\t\t{:.2f} sec'.format(cnt,cur_work.obj,cur_work.obj+cur_work.plt,work.obj,cur_work.avg_wt(gap),cur_time-start_time),flush=True)
        elif cur_time - disp_time > INTVL_TIME:
            print('{}\t{:g} ({:g})\t{:g}\t{:g}\t\t{:.2f} sec'.format(cnt,cur_work.obj,cur_work.obj+cur_work.plt,work.obj,cur_work.avg_wt(gap),cur_time-start_time),flush=True)
            disp_time = time.time()


# --------------------------------------------------------------------
#   initialize penalty weight
#
#   gap(I): GAP data
#   work(I/O): working data
# --------------------------------------------------------------------
def init_weight(gap, work):
    for i in range(gap.num_agent):
        for j in range(gap.num_job):
            if (gap.cost)[i][j] > (work.wt)[i]:
                (work.wt)[i] = (gap.cost)[i][j]
    # update weighted penalty
    work.calc_plt(gap)


# --------------------------------------------------------------------
#   update penalty weight
#
#   gap(I): GAP data
#   work(I/O): working data
#   th(I): threshold
# --------------------------------------------------------------------
def update_weight(gap, work, th):
    if work.obj + work.plt > th - NUM_EPSILON:
        # decrease penalty weight
        for i in range(gap.num_agent):
            (work.wt)[i] = max(NUM_EPSILON, (1.0 - DEC_WT_RATIO) * (work.wt)[i])
    else:
        # increase penalty weight
        max_plt = 0.0
        for i in range(gap.num_agent):
            if (work.used)[i] - (gap.cap)[i] > max_plt:
                max_plt = (work.used)[i] - (gap.cap)[i]
        for i in range(gap.num_agent):
            (work.wt)[i] *= 1.0 + INC_WT_RATIO * max(0, (work.used)[i] - (gap.cap)[i]) / max_plt
    # update weighted penalty
    work.calc_plt(gap)


# --------------------------------------------------------------------
#   local search
#
#   gap(I): GAP data
#   work(I/O): working data
#   cur_work(I/O): current working data
#   return: found feasible solution in LS -> True
# --------------------------------------------------------------------
def local_search(gap,work,cur_work):
    # local search
    while True:
        # shift neighborhood search
        shift_nb_search(gap,work,cur_work)
        # swap neighborhood search
        if swap_nb_search(gap,work,cur_work):
            continue
        break


# --------------------------------------------------------------------
#   shift neighborhood search
#
#   gap(I): GAP data
#   work(I/O): working data
#   cur_work(I/O): current working data
#   return: obtain improved solution -> True
# --------------------------------------------------------------------
def shift_nb_search(gap,work,cur_work):
    # calculate difference for shift operation
    def calc_diff(gap,work,j,i):
        i1,i2 = (work.sol)[j],i
        delta_obj = (gap.cost)[i2][j] - (gap.cost)[i1][j]
        cur_plt = max(0, (work.used)[i1] - (gap.cap)[i1])
        new_plt = max(0, (work.used)[i1] - (gap.res)[i1][j] - (gap.cap)[i1])
        delta_plt_i1 = (work.wt)[i1] * (new_plt - cur_plt)
        cur_plt = max(0, (work.used)[i2] - (gap.cap)[i2])
        new_plt = max(0, (work.used)[i2] + (gap.res)[i2][j] - (gap.cap)[i2])
        delta_plt_i2 = (work.wt)[i2] * (new_plt -  cur_plt)
        delta_plt = delta_plt_i1 + delta_plt_i2
        return delta_obj, delta_plt

    # update solution by shift operation
    def update_sol(gap,work,j,i):
        i1,i2 = (work.sol)[j],i
        (work.sol)[j] = i2
        (work.used)[i1] -= (gap.res)[i1][j]
        (work.used)[i2] += (gap.res)[i2][j]
        work.obj += (gap.cost)[i2][j] - (gap.cost)[i1][j]
        work.calc_plt(gap)
        (work.job)[i1].remove(j)
        (work.job)[i2].add(j)

    # shift neighborhood search
    improved = False
    restart = True
    while restart:
        restart = False
        nbhd = ((j,i)
                for j in range(gap.num_job)
                for i in range(gap.num_agent) if i != (cur_work.sol)[j])
        for j,i in nbhd:
            # calculate difference
            delta_obj, delta_plt = calc_diff(gap,cur_work,j,i)
            # (i) first feasible solution or (ii) improved feasible solution
            if cur_work.plt + delta_plt < NUM_EPSILON and (work.plt > NUM_EPSILON  or cur_work.obj + delta_obj < work.obj - NUM_EPSILON):
                # update incumbent solution
                work.copy(cur_work)
                update_sol(gap,work,j,i)
                #print('*',flush=True,end='')
            obj,plt = cur_work.obj, cur_work.plt
            if delta_obj + delta_plt < -NUM_EPSILON:
                # update current solution
                update_sol(gap,cur_work,j,i)
                assert abs(obj + plt + delta_obj + delta_plt - cur_work.obj - cur_work.plt) < NUM_EPSILON, (obj, plt, delta_obj+delta_plt, cur_work.obj, cur_work.plt)
                #print('.',flush=True,end='')
                improved = restart = True
                break
    return improved


# --------------------------------------------------------------------
#   swap neighborhood search
#
#   gap(I): GAP data
#   work(I/O): working data
#   cur_work(I/O): current working data
#   return: obtain improved solution -> True
# --------------------------------------------------------------------
def swap_nb_search(gap,work,cur_work):
    # calculate difference for swap operation
    def calc_diff(gap,work,j1,j2):
        i1,i2 = (work.sol)[j1],(work.sol)[j2]
        delta_obj = (gap.cost)[i2][j1] + (gap.cost)[i1][j2] - (gap.cost)[i1][j1] - (gap.cost)[i2][j2]
        cur_plt = max(0, (work.used)[i1] - (gap.cap)[i1])
        new_plt = max(0, (work.used)[i1] - (gap.res)[i1][j1] + (gap.res)[i1][j2] - (gap.cap)[i1])
        delta_plt_i1 = (work.wt)[i1] * (new_plt - cur_plt)
        cur_plt = max(0, (work.used)[i2] - (gap.cap)[i2])
        new_plt = max(0, (work.used)[i2] - (gap.res)[i2][j2] + (gap.res)[i2][j1] - (gap.cap)[i2])
        delta_plt_i2 = (work.wt)[i2] * (new_plt - cur_plt)
        delta_plt = delta_plt_i1 + delta_plt_i2
        return delta_obj, delta_plt

    # update solution by swap operation
    def update_sol(gap,work,j1,j2):
        i1,i2 = (work.sol)[j1],(work.sol)[j2]
        (work.sol)[j1], (work.sol)[j2] = i2, i1
        (work.used)[i1] += (gap.res)[i1][j2] - (gap.res)[i1][j1]
        (work.used)[i2] += (gap.res)[i2][j1] - (gap.res)[i2][j2]
        work.obj += (gap.cost)[i2][j1] + (gap.cost)[i1][j2] - (gap.cost)[i1][j1] - (gap.cost)[i2][j2]
        work.calc_plt(gap)
        (work.job)[i1].remove(j1)
        (work.job)[i2].add(j1)
        (work.job)[i2].remove(j2)
        (work.job)[i1].add(j2)

    # swap neighborhood search
    #nbhd = ((j1,j2)
    #        for j1 in range(gap.num_job)
    #        for j2 in range(j1+1,gap.num_job) if (cur_work.sol)[j2] != (cur_work.sol)[j1])
    nbhd = ((j1,j2)
            for i in range(gap.num_agent) if (cur_work.used)[i] > (gap.cap)[i]
            for j1 in (cur_work.job)[i]
            for j2 in range(j1+1,gap.num_job) if (cur_work.sol)[j2] != (cur_work.sol)[j1])
    for j1,j2 in nbhd:
        # calculate difference
        delta_obj,delta_plt = calc_diff(gap,cur_work,j1,j2)
        # (i) first feasible solution or (ii) improved feasible solution
        if cur_work.plt + delta_plt < NUM_EPSILON and (work.plt > NUM_EPSILON or cur_work.obj + delta_obj < work.obj - NUM_EPSILON):
            # update incumbent solution
            work.copy(cur_work)
            update_sol(gap,work,j1,j2)
            #print('*',flush=True,end='')
        obj,plt = cur_work.obj, cur_work.plt
        if delta_obj + delta_plt < -NUM_EPSILON:
            # update current solution
            update_sol(gap,cur_work,j1,j2)
            assert abs(obj + plt + delta_obj+delta_plt - cur_work.obj - cur_work.plt) < NUM_EPSILON, (obj, plt, delta_obj+delta_plt, cur_work.obj, cur_work.plt)
            #print(':',flush=True,end='')
            return True
    return False


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

    # set random seed
    random.seed(RANDOM_SEED)

    # set starting time
    start_time = time.time()

    # read instance
    gap = Gap()
    gap.read(args)
    gap.write()

    # solve GAP
    work = Work(gap)
    weight_local_search(gap, work, args.time)  # weighting local search
    work.write(gap)

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
