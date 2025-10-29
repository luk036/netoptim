from math import log

import networkx as nx
import numpy as np
import pytest
from digraphx.tiny_digraph import DiGraphAdapter
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell
from mywheel.map_adapter import MapAdapter

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


def form_graph(T, pos, eta, seed=None):
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
    gra = nx.random_geometric_graph(n, eta, pos=pos)
    gra = nx.DiGraph(gra)
    gra = DiGraphAdapter(gra)
    return gra


def create_random_graph():
    N = 75
    M = 20
    T = N + M
    xbase = 2
    ybase = 3
    x = [i for i in vdcorput(T, xbase)]
    y = [i for i in vdcorput(T, ybase)]
    pos = zip(x, y)
    gra = form_graph(T, pos, 1.6, seed=5)

    for utx, vtx in gra.edges():
        h = np.array(gra.nodes()[utx]["pos"]) - np.array(gra.nodes()[vtx]["pos"])
        distance = np.log(np.sqrt(h.dot(h)))
        gra[utx][vtx]["cost"] = (distance, distance)
    return gra


def create_fixed_graph():
    gra = MapAdapter(
        [
            {
                2: (log(22.0), log(125.0)),
                3: (log(16.0), log(18.0)),
                4: (log(15.0), log(11.0)),
            },
            {
                1: (log(10.0), log(10.0)),
                2: (log(20.0), log(19.0)),
                3: (log(14.0), log(12.0)),
                4: (100, log(21.0)),
            },
            {
                0: (log(125.0), log(22.0)),
                1: (log(19.0), log(20.0)),
                2: (log(13.0), log(13.0)),
            },
            {
                0: (log(18.0), log(16.0)),
                1: (log(12.0), log(14.0)),
                4: (log(24.0), log(23.0)),
            },
            {
                0: (log(11.0), log(15.0)),
                1: (log(21.0), -100),
                3: (log(23.0), log(24.0)),
                4: (log(17.0), log(17.0)),
            },
        ]
    )
    return gra


def get_cost(edge):
    return edge["cost"] if isinstance(edge, dict) else edge


@pytest.mark.parametrize("graph_creator", [create_random_graph, create_fixed_graph])
def test_optscaling(graph_creator):
    gra = graph_creator()
    if isinstance(gra, DiGraphAdapter):
        cmax = max(cost[0] for _, _, cost in gra.edges.data("cost"))
        cmin = min(cost[0] for _, _, cost in gra.edges.data("cost"))
    else:
        cmax = log(125.0)
        cmin = log(10.0)

    xinit = np.array([cmax, cmin])
    t = cmax - cmin
    ellip = Ell(1.5 * t if isinstance(gra, DiGraphAdapter) else 200 * t, xinit)
    dist = list(0 for _ in gra)
    omega = OptScalingOracle(gra, dist, get_cost)
    xbest, _, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None
