import numpy as np

from copy import copy

class NBox:
    def __init__(self, boundaries):
        self.boundaries = boundaries
        self.N = len(self.boundaries)

    def split(self):
        dim = np.random.randint(self.N)

        x0, x1 = self.boundaries[dim]
        mid = (x0 + x1) / 2

        bounds0 = copy(self.boundaries)
        bounds1 = copy(self.boundaries)

        bounds0[dim, :] = x0, mid
        bounds1[dim, :] = mid, x1

        return NBox(bounds0), NBox(bounds1)

    def sample_point(self):
        x, y = self.boundaries[:, 0], self.boundaries[:, 1]
        return x + (y - x) * np.random.random([self.N])

def generate_points(b0, num_leafs):
    boxes = [b0]
    for _ in range(num_leafs - 1):
        b = boxes.pop(np.random.choice(len(boxes)))
        boxes.extend(b.split())

    return [b.sample_point() for b in boxes]

if __name__ == '__main__':
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    from sklearn import decomposition

    num_points = 1000
    N_dim = 4
    points = list(generate_points(NBox(np.array([[0, 1.0] for _ in range(N_dim)])), num_points))

    coords = np.array(points)

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')

    pca = decomposition.PCA(n_components=2)

    reduced = pca.fit_transform(coords)

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #ax.scatter(*reduced.T, s=1)

    plt.scatter(*reduced.T, s=5)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("N={} dimensions, {} points".format(N_dim, num_points))
    plt.show()
    