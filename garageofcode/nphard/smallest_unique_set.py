import time
from itertools import chain, combinations
from collections import Counter

import numpy as np

def get_data(n, k, b):
    """returns n random sets of length k
    with elements from 0..b-1
    """

    for _ in range(n):
        yield set(np.random.randint(0, b, size=k))


def powerset(s):
    s = list(s)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def smallest_unique_set(S, subset=None):
    """Naive version"""

    if subset is None:
        subset = set(chain.from_iterable(S))
    for si in S:
        if not subset - set(si):
            raise ValueError("No unique set exists")
    p = []
    while S:
        c = Counter(chain.from_iterable(S))
        if subset - set(c):
            r = next(iter(subset - set(c)))
            p.append(r)
            break        
        else:
            r = c.most_common()[-1][0]
            p.append(r)
            S = [si for si in S if r in si]
    return p


def smallest_unique_set_exhaustive(S, subset=None):
    """Exhaustive version"""

    if subset is None:
        subset = set(chain.from_iterable(S))
    for si in S:
        if not subset - set(si):
            raise ValueError("No unique set exists")

    for s in powerset(subset):
        s = set(s)
        for si in S:
            if not s - si:
                break
        else:
            return s


def main():
    #S = [[1, 2], [1, 2, 3], [1, 3], [2, 3], [3, 4]]
    S = [si for si in get_data(100000, 500, 10000)]
    t0 = time.time()
    naive = smallest_unique_set(S)
    t1 = time.time()
    print("Naive:", naive)
    print("Naive len:", len(naive))
    print("Naive time: {0:.3f}".format(t1 - t0))
    '''
    t0 = time.time()
    exhaustive = smallest_unique_set_exhaustive(S)
    t1 = time.time()
    print("Exhaustive:", exhaustive)
    print("Exhaustive len:", len(exhaustive))
    print("Exhaustive time: {0:.3f}".format(t1 - t0))
    '''


if __name__ == '__main__':
    main()

    #for elem in get_data(100, 5, 7):
    #    print(elem)