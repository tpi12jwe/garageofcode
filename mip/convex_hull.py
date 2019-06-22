from itertools import product
import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt

from solver import get_solver, status2str

tol = 1e-4

def draw_planes(ax, planes):
    t = np.linspace(-10, 10)
    eps = 0.05

    for plane in planes:
        a, b, d = plane
        assert abs(a + b) > tol
        x = -d/(a + b) + b*t
        y = -d/(a + b) - a*t
        ax.plot(x, y, color='b')
        x_p = x + np.sign(a) * eps
        y_p = y + np.sign(b) * eps
        ax.plot(x_p, y_p, color='r')

def is_inside(point, planes):
    A, d = planes[:, :-1], planes[:, -1]
    proj = np.matmul(A, point) + d
    return np.all(proj >= 0)

def make_plane(points, ref):
    """
    Make a plane with a normal that is orthogonal 
    to all (u - v) where u and v are in points
    The plane intersects all points
    The plane is oriented such that the point
    ref will have a positive value
    """

    p0 = points[0]
    A = np.matrix([p_i - p0 for p_i in points[1:]])
    normal = linalg.null_space(A)
    d = -np.dot(p0, normal)
    sgn = np.dot(ref, normal) + d
    normal *= sgn
    d *= sgn

    plane = np.concatenate([normal.T[0], d])
    return plane

def is_bounded(planes):
    R = 1000
    tol = 1e-6

    if not len(planes):
        return False

    solver = get_solver("CBC")

    X = [solver.NumVar(lb=-R, ub=R) for _ in range(len(planes[0]) - 1)]

    obj = 0
    for A in planes:
        #print(A)
        a, d = A[:-1], A[-1]
        proj = solver.Dot(a, X)
        obj += proj * np.random.random()
        solver.Add(proj >= -d)

    #solver.Add(X[0] <= 1)
    #solver.Add(X[0] >= -1)

    #obj = solver.Dot(np.sum(planes[:, :-1], axis=0), X)

    solver.SetObjective(obj, maximize=True)
    result = solver.Solve(time_limit=10)
    result = status2str[result]
    if result == "INFEASIBLE":
        print("Infeasible!")
        return True
    else:
        sol = [solver.solution_value(x) for x in X]
        print(sol)
        if any([np.abs(y - R) < tol for y in sol]):
            print("Unbounded")
        else:
            print("Bounded")
    print()

def main():
    '''
    for _ in range(1000):
        A = np.random.random([5, 3]) - 0.5
        #A = np.array([[1, -1],
        #              [-1, -1]])

        #print(A)
        is_bounded(A)
    '''

    points = np.random.random([10, 2])*10 - 5

    c0 = np.random.choice(len(points), 3, replace=False)
    c = [points[ch] for ch in c0]

    plane1 = make_plane([c[0], c[1]], c[2])
    plane2 = make_plane([c[0], c[2]], c[1])
    plane3 = make_plane([c[1], c[2]], c[0])

    planes = np.array([plane1, plane2, plane3])

    fig, ax = plt.subplots()

    for x, y in product(np.linspace(-10, 10, 20), repeat=2):
        col = 'r' if is_inside([x, y], planes) else 'b'
        ax.scatter(x, y, color=col)

    draw_planes(ax, planes)

    plt.show()


    #planes = np.random.random([3, 3]) - 0.5
    #point = np.array([[0], [0]])

    #points = np.array([[1, 0], [0, 1]])
    #ref = [0, 0]

    #make_plane(points, ref)

    '''
    '''

    #for _ in range(100):
    #    print("is inside:", is_inside(point, planes))


if __name__ == '__main__':
    main()