from math import log
from typing import Any, Callable, Dict, List, Tuple, Union

import networkx as nx
import numpy as np
import pytest
from digraphx.tiny_digraph import DiGraphAdapter
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell
from ellalgo.ell_config import Options
from mywheel.map_adapter import MapAdapter

from netoptim import DEFAULT_TOLERANCE, solve_opt_scaling
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


def create_random_graph() -> DiGraphAdapter:
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


def create_fixed_graph() -> MapAdapter:
    gra: MapAdapter = MapAdapter(
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


def get_cost(
    edge: Union[Dict[str, Any], Tuple[float, float]],
) -> Union[Dict[str, Any], Tuple[float, float]]:
    return edge["cost"] if isinstance(edge, dict) else edge


@pytest.mark.parametrize("graph_creator", [create_random_graph, create_fixed_graph])
def test_optscaling(
    graph_creator: Callable[[], Union[DiGraphAdapter, MapAdapter]],
) -> None:
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
    dist: List[float] = [0.0 for _ in gra]
    omega = OptScalingOracle(gra, dist, get_cost)
    xbest, _, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None


def test_ratio_make_weight_fn_matches_eval() -> None:
    gra = create_fixed_graph()
    ratio = OptScalingOracle.Ratio(gra, get_cost)
    x = np.array([1.25, -0.5])
    weight = ratio.make_weight_fn(x)
    checked = 0
    for utx in gra:
        for _, edge in gra[utx].items():
            assert weight(edge) == ratio.eval(edge, x)
            checked += 1
    assert checked > 0


def _build_fixed_problem() -> Tuple[OptScalingOracle, Ell]:
    gra = create_fixed_graph()
    cmax = log(125.0)
    cmin = log(10.0)
    t = cmax - cmin
    ellip = Ell(200 * t, np.array([cmax, cmin]))
    dist: List[float] = [0.0 for _ in gra]
    return OptScalingOracle(gra, dist, get_cost), ellip


def test_solve_opt_scaling_default_tolerance_matches_tight() -> None:
    assert DEFAULT_TOLERANCE == 1e-8

    omega_default, ellip_default = _build_fixed_problem()
    x_default, gamma_default, niter_default = solve_opt_scaling(
        omega_default, ellip_default, float("inf")
    )

    tight = Options()
    tight.tolerance = 1e-20
    omega_tight, ellip_tight = _build_fixed_problem()
    x_tight, gamma_tight, niter_tight = solve_opt_scaling(
        omega_tight, ellip_tight, float("inf"), tight
    )

    assert x_default is not None and x_tight is not None
    assert np.isclose(gamma_default, gamma_tight, atol=1e-3)
    assert np.allclose(x_default, x_tight, atol=1e-3)
    assert niter_default <= niter_tight
