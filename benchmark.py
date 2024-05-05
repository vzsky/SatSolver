from random import sample

def ForLoop(s):
    result = []
    for e in s: 
        if len(result) == 2: break
        result.append(e)
    return result

def SetDestruct(s):
    if len(s) >= 2: 
        a, b, *_ = s
        return set([a, b])
    if len(s) == 1: 
        a, *_ = s
        return set([a])
    return set()

from simple_benchmark import benchmark

b = benchmark([ForLoop, SetDestruct],
              {i: set([i]) for i in range(0, 10)},
              argument_name='set size')

import matplotlib.pyplot as plt
b.plot()
plt.savefig('benchmark.png')
