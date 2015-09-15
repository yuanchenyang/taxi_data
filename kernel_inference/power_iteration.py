import numpy as np
import scipy.linalg as sla

def rand_dist(n):
    dist = np.random.sample(n)
    return dist / sum(dist)

def rand_sto_mat(n):
    '''Generates a random column-stochastic nxn matrix'''
    return np.array([rand_dist(n) for _ in range(n)]).T

def norm(vec, p=2):
    '''Normalizes vec using the L-p norm'''
    return vec / np.linalg.norm(vec, 1)

def get_nth_eigens(m, n=0, p=1):
    '''Returns n-th largest eigenvector and eigenvalue, L-p normalized.'''
    evals, evecs = sla.eig(m, right=True)
    index, evl = sorted(enumerate(evals), key=lambda x: abs(x[1]), reverse=True)[n]
    ev = np.real(evecs[:,index])
    return evl, norm(ev / ev[0])

def power_iter(m, niters=100):
    v  = rand_dist(np.shape(m)[0])
    for _ in range(niters):
        v = norm(m.dot(v))
    return v

def nth_eigen_iter(m, n=0, niters=100):
    '''Find the n-th highest eigenvector using power iteration'''
    ev = power_iter(m)
    evl = np.mean(m.dot(ev) / ev)
    for _ in range(n):
        m = m - evl * ev.dot(ev.T)
        ev = power_iter(m)
        evl = np.mean(m.dot(ev) / ev)
    return evl, norm(ev / ev[0])
