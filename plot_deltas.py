import pickle
import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import expon
from collections import defaultdict
from pdb import set_trace as T

deltas = pickle.load(open('figures/deltas.pkl'))

points = defaultdict(int)

for d in deltas:
    if d != 0:
        points[d] += 1

x, y = zip(*sorted(points.items()))

total = sum(i for i in y)

mean = float(sum(xi * yi for xi, yi in zip(x, y))) / total

# Normalize y
y = [float(i) / total for i in y]

ex = np.linspace(expon.ppf(0.01), expon.ppf(0.99), 100)

#plt.hist(deltas, bins = 100)
plt.scatter(x, y)
plt.plot(x, expon.pdf(x, loc=0, scale=mean), color='r')

plt.xlim(0, 200)
plt.ylim(0, 0.08)

plt.xlabel('Interarrival time (s)')
plt.ylabel('Fraction of passengers')

plt.savefig('figures/trip_time_deltas.pdf', format="pdf", transparent=True, bbox_inches="tight")
