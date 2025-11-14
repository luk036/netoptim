from typing import Any, Dict

import pytest
from digraphx.neg_cycle import NegCycleFinder
from digraphx.neg_cycle_q import NegCycleFinderQ
from ellalgo.cutting_plane import bsearch
from ellalgo.ell_config import Options
from ellalgo.ell_typing import OracleBS
from pytest import approx

MAX_ITERS = 2000
TOLERANCE = 1e-14

Finders = [NegCycleFinder, NegCycleFinderQ]


def run_lawler_TCP(finder, dist, TCP) -> bool:
    if isinstance(finder, NegCycleFinderQ):
        for _ in finder.howard_succ(
            dist,
            lambda e: TCP - e["delay"] if e["type"] == "s" else e["delay"],
            lambda _, __: True,
        ):
            return True
    else:
        for _ in finder.howard(
            dist, lambda e: TCP - e["delay"] if e["type"] == "s" else e["delay"]
        ):
            return True
    return False


# def run_lawler_even(finder, dist, beta) -> bool:
#     if isinstance(finder, NegCycleFinderQ):
#         for _ in finder.howard_succ(dist, lambda edge: edge - beta, lambda _, __: True):
#             return True
#     else:
#         for _ in finder.howard(dist, lambda edge: edge - beta):
#             return True
#     return False


# def run_lawler_prop(finder, dist, beta) -> bool:
#     if isinstance(finder, NegCycleFinderQ):
#         for _ in finder.howard_succ(
#             dist, lambda edge: edge["cost"] - beta * edge["time"], lambda _, __: True
#         ):
#             return True
#     else:
#         for _ in finder.howard(dist, lambda edge: edge["cost"] - beta * edge["time"]):
#             return True
#     return False


@pytest.mark.parametrize("finder_class", Finders)
def test_minimize_TCP(finder_class):
    dist: Dict[str, int] = {"v1": 0, "v2": 0, "v3": 0}
    Digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v1": {"v2": {"type": "s", "delay": 7}, "v3": {"type": "h", "delay": 2}},
        "v2": {"v1": {"type": "h", "delay": 4}, "v3": {"type": "p", "delay": 0}},
        "v3": {"v1": {"type": "s", "delay": 3}},
    }

    def has_negative_cycle(TCP, dist) -> bool:
        finder = finder_class(Digraph)
        return run_lawler_TCP(finder, dist, TCP)

    class MyBSOracle(OracleBS):
        def assess_bs(self, gamma: float) -> bool:
            return not has_negative_cycle(gamma, dist)

    omega = MyBSOracle()
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (0.0, 8.0), options)
    print(opt, num_iter)
    assert opt == approx(5.0)
    assert num_iter <= 50
    # assert dist == {"v1": 2, "v2": 0, "v3": 0}


# @pytest.mark.parametrize("finder_class", Finders)
# def test_maximize_slack(finder_class):
#     dist: Dict[str, int] = {"v1": 0, "v2": 0, "v3": 0}
#     TCP = 4.5
#     Digraph: Dict[str, Dict[str, float]] = {
#         "v1": {"v2": TCP - 2, "v3": 1.5},
#         "v2": {"v3": TCP - 3, "v1": 2.0},
#         "v3": {"v1": TCP - 4, "v2": 3.0},
#     }

#     def has_negative_cycle_EVEN(beta, dist) -> bool:
#         finder = finder_class(Digraph)
#         return run_lawler_even(finder, dist, beta)

#     class MyBSOracle2(OracleBS):
#         def assess_bs(self, gamma: float) -> bool:
#             return has_negative_cycle_EVEN(gamma, dist)

#     omega = MyBSOracle2()
#     options = Options()
#     options.tolerance = TOLERANCE
#     opt, num_iter = bsearch(omega, (0.0, 10.0), options)
#     print(opt, num_iter)
#     assert opt == approx(1.0)
#     assert num_iter <= 50


# @pytest.mark.parametrize("finder_class", Finders)
# def test_maximize_effective_slack(finder_class):
#     dist: Dict[str, int] = {"v1": 0, "v2": 0, "v3": 0}
#     TCP = 4.5
#     Digraph: Dict[str, Dict[str, Dict[str, float]]] = {
#         "v1": {"v2": {"cost": TCP - 2, "time": 3.1}, "v3": {"cost": 1.5, "time": 0.7}},
#         "v2": {"v3": {"cost": TCP - 3, "time": 4.1}, "v1": {"cost": 2.0, "time": 2.2}},
#         "v3": {"v1": {"cost": TCP - 4, "time": 5.1}, "v2": {"cost": 3.0, "time": 1.5}},
#     }

#     def has_negative_cycle_PROP(beta, dist) -> bool:
#         finder = finder_class(Digraph)
#         return run_lawler_prop(finder, dist, beta)

#     class MyBSOracle3(OracleBS):
#         def assess_bs(self, gamma: float) -> bool:
#             return has_negative_cycle_PROP(gamma, dist)

#     omega = MyBSOracle3()
#     options = Options()
#     options.tolerance = TOLERANCE
#     opt, num_iter = bsearch(omega, (0.0, 10.0), options)
#     print(opt, num_iter)
#     assert opt == approx(0.3448275862069039)
#     assert num_iter <= 50
