from typing import Any, Dict, List, Tuple, Union

import networkx as nx
import numpy as np
from digraphx.tiny_digraph import DiGraphAdapter
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell

from netoptim.optscaling_oracle import OptScalingOracle


def vdc(n: int, base: int = 2) -> float:
    """[summary]

    Arguments:
        n (int): [description]

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        float: [description]
    """
    vdc, denom = 0.0, 1.0
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc


def vdcorput(n: int, base: int = 2) -> List[float]:
    """[summary]

    Arguments:
        n (int): [description]

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        List[float]: [description]
    """
    return [vdc(i, base) for i in range(n)]


def form_graph(T: float, pos: Any, eta: float, seed: Any = None) -> DiGraphAdapter:
    """Form N by N grid of nodes, connect nodes within eta.
        mu and eta are relative to 1/(N-1)

    Args:
        T (float): Total number of nodes.
        pos (Any): Node positions.
        eta (float): Threshold for connecting nodes.
        seed (Any, optional): Seed for random number generator. Defaults to None.

    Returns:
        DiGraphAdapter: The generated graph.
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


def create_large_random_graph() -> DiGraphAdapter:
    N = 200
    M = 50
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


def get_cost(
    edge: Union[Dict[str, Any], Tuple[float, float]],
) -> Union[Dict[str, Any], Tuple[float, float]]:
    return edge["cost"] if isinstance(edge, dict) else edge


def test_optscaling_stress() -> None:
    gra = create_large_random_graph()
    cmax = max(cost[0] for _, _, cost in gra.edges.data("cost"))
    cmin = min(cost[0] for _, _, cost in gra.edges.data("cost"))

    xinit = np.array([cmax, cmin])
    t = cmax - cmin
    ellip = Ell(1.5 * t, xinit)
    dist: List[float] = list(0 for _ in gra)
    omega = OptScalingOracle(gra, dist, get_cost)
    xbest, _, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None
