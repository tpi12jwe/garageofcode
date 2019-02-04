import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import random
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import transpose, flatten_simple
from mip.solver import get_solver, solution_value

def make_min_times_constraint(solver, student2time2take, min_times):
    for student, time2take in enumerate(student2time2take):
        solver.Add(solver.Sum(time2take) >= min_times[student])
    
def make_max_simultaneous_constraint(solver, student2time2take, max_simultaneous):
    for time, student2take in enumerate(transpose(student2time2take)):
        solver.Add(solver.Sum(student2take) >= max_simultaneous[time])

def make_availability_constraint(solver, student2time2take, available):
    for student, time2take in enumerate(student2time2take):
        for time, take in enumerate(time2take):
            solver.Add(take <= available[student][time])

def get_total_workdays(solver, student2time2take, D, T_D):
    works_days = [solver.IntVar(0, 1) for _ in range(D)]

    time2student2take = list(transpose(student2time2take))

    for d, works_day in enumerate(works_days):
        student2take = time2student2take[d*T_D:(d+1)*T_D]
        student2take = flatten_simple(student2take)
        for take in student2take:
            solver.Add(works_day >= take)

def get_total_time_span(solver, student2time2take, D, T_D):
    start_time_day = [solver.NumVar(lb=0) for _ in range(D)]
    end_time_day = [solver.NumVar(ub=T_D-1) for _ in range(D)]

    time2student2take = list(transpose(student2time2take))

    for d, start_time, end_time in enumerate(zip(start_time_day, end_time_day)):
        for t in range(T_D):
            any_take = solver.IntVar(0, 1)
            for take in time2student2take[d*T_D+t]:
                solver.Add(any_take >= take)
            solver.Add(start_time <= any_take * t)
            solver.Add(end_time >= any_take * t)

    time_span_day = [et - st for st, et in zip(start_time_day, end_time_day)]

    return solver.Sum(time_span_day)

def draw_tutoring_schedule(ax, student2time2take, available, D, T_D):
    T = D * T_D
    N = len(student2time2take) + 1
    # Draw time and date lines
    for y in range(N):
        if y == 1:
            linewidth = 3 # teacher's line
        else:
            linewidth = 1
        ax.plot([0, T], [y, y], c='k', linewidth=linewidth)

    for x in range(T + 1):
        if x % T_D == 0:
            linewidth = 3 # date line
        else:
            linewidth = 1
        ax.plot([x, x], [0, N], c='k', linewidth=linewidth)

    # Draw student's schedules and available
    for student, time2take in enumerate(student2time2take):
        for time, take in enumerate(time2take):
            if take:
                patch = Rectangle((student + 1, time), 1, 1, alpha='1.0', facecolor='b')
            elif available[student][time]:
                patch = Rectangle((student + 1, time), 1, 1, alpha='0.3', facecolor='b')
            ax.add_patch(patch)

def main():
    # Set params and generate random data
    D = 5 # num days
    T_D = 10 # num times per day
    T = D * T_D
    N = 10 # num students
    max_simultaneous = [3 for _ in range(T)] # max num student per time
    min_times = [1 for _ in range(N)] # min times per student

    available = [[random.random() < 0.5 for _ in range(T)] for _ in range(N)]

    # Preference parameters
    per_diem_cost = 100
    time_cost = 30

    # Generate variables
    solver = get_solver("CBC")

    student2time2take = [[solver.IntVar(0, 1) for _ in range(T)] for _ in range(N)]

    # Add constraints
    make_availability_constraint(solver, student2time2take, available)
    make_min_times_constraint(solver, student2time2take, min_times)
    make_max_simultaneous_constraint(solver, student2time2take, max_simultaneous)

    # Add costs and values
    obj = 0
    obj -= get_total_workdays(solver, student2time2take, D, T_D) * per_diem_cost
    obj -= get_total_time_span(solver, student2time2take, D, T_D) * time_cost

    solver.SetObjective(obj, maximize=True)

    solver.Solve()

    student2time2take_solve = [[solution_value(take) for take in time2take] 
                                            for time2take in student2time2take]

    fig, ax = plt.subplots()
    draw_tutoring_schedule(ax, student2time2take)
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    main()