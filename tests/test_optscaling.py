# -*- coding: utf-8 -*-
from __future__ import print_function

import networkx as nx
import numpy as np
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell

from netoptim.optscaling_oracle import OptScalingOracle


def vdc(n, base=2):
    """[summary]

    Arguments:
        n ([type]): [description]

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        [type]: [description]
    """
    vdc, denom = 0.0, 1.0
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc


def vdcorput(n, base=2):
    """[summary]

    Arguments:
        n ([type]): [description]

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        [type]: [description]
    """
    return [vdc(i, base) for i in range(n)]


def formGraph(T, pos, eta, seed=None):
    """Form N by N grid of nodes, connect nodes within eta.
        mu and eta are relative to 1/(N-1)

    Arguments:
        t (float): [description]
        pos ([type]): [description]
        eta ([type]): [description]

    Keyword Arguments:
        seed ([type]): [description] (default: {None})

    Returns:
        [type]: [description]
    """
    if seed:
        np.random.seed(seed)

    N = np.sqrt(T)
    eta = eta / (N - 1)

    # generate perterbed grid positions for the nodes
    pos = dict(enumerate(pos))
    n = len(pos)

    # connect nodes with edges
    G = nx.random_geometric_graph(n, eta, pos=pos)
    G = nx.DiGraph(G)
    # G.add_node('dummy', pos = (0.3, 0.4))
    # G.add_edge('dummy', 1)
    # G.nodemap = {v : i_v for i_v, v in enumerate(G.nodes())}
    return G


N = 75
M = 20
T = N + M
xbase = 2
ybase = 3
x = [i for i in vdcorput(T, xbase)]
y = [i for i in vdcorput(T, ybase)]
pos = zip(x, y)
G = formGraph(T, pos, 1.6, seed=5)
# for u, v in G.edges():
#     h = np.array(G.nodes()[u]['pos']) - np.array(G.nodes()[v]['pos'])
#     G[u][v]['cost'] = np.sqrt(h @ h)

for u, v in G.edges():
    h = np.array(G.nodes()[u]["pos"]) - np.array(G.nodes()[v]["pos"])
    G[u][v]["cost"] = np.log(np.sqrt(h @ h))

cmax = max(c for _, _, c in G.edges.data("cost"))
cmin = min(c for _, _, c in G.edges.data("cost"))


def get_cost(e):
    u, v = e
    return G[u][v]["cost"]


def test_optscaling():
    """[summary]

    Keyword Arguments:
        duration (float): [description] (default: {0.000001})

    Returns:
        [type]: [description]
    """
    xinit = np.array([cmax, cmin])
    t = cmax - cmin
    ellip = Ell(1.5 * t, xinit)
    dist = list(0 for _ in G)
    omega = OptScalingOracle(G, dist, get_cost)
    xbest, _, _ = cutting_plane_optim(omega, ellip, float("inf"))
    # fmt = '{:f} {} {} {}'
    # print(np.exp(xbest))
    # print(fmt.format(np.exp(fb), niter, feasible, status))
    assert xbest is not None
    # return ell_info.num_iters
