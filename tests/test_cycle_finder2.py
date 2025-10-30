import pytest
from digraphx.neg_cycle import NegCycleFinder
from digraphx.neg_cycle_q import NegCycleFinderQ
from pytest import approx
from ellalgo.cutting_plane import bsearch
from ellalgo.ell_typing import OracleBS
from ellalgo.ell_config import Options
from icecream import ic

MAX_ITERS = 100
TOLERANCE = 1e-7

finders = [NegCycleFinder, NegCycleFinderQ]


def run_lawler_TCP2(finder, dist):
    if isinstance(finder, NegCycleFinderQ):
        for _ in finder.howard_succ(dist, lambda edge: edge, lambda _, __: True):
            return True
    else:
        for _ in finder.howard(dist, lambda edge: edge):
            return True
    return False


def run_lawler_even2(finder, dist, beta):
    if isinstance(finder, NegCycleFinderQ):
        for _ in finder.howard_succ(dist, lambda edge: edge - beta, lambda _, __: True):
            return True
    else:
        for _ in finder.howard(dist, lambda edge: edge - beta):
            return True
    return False


def run_lawler_prop2(finder, dist, beta):
    if isinstance(finder, NegCycleFinderQ):
        for _ in finder.howard_succ(dist, lambda edge: edge["cost"] - beta * edge["time"], lambda _, __: True):
            return True
    else:
        for _ in finder.howard(dist, lambda edge: edge["cost"] - beta * edge["time"]):
            return True
    return False


@pytest.mark.parametrize("finder_class", finders)
def test_minimize_TCP2(finder_class):
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}

    def has_negative_cycle(TCP, dist):
        """Creates a test graph for timing tests."""
        digraph = {
            "v0": {"v3": TCP - 6, "v2": 6},
            "v1": {"v2": TCP - 9, "v4": 3},
            "v2": {"v0": TCP - 7, "v1": 6},
            "v3": {"v4": TCP - 8, "v0": 6},
            "v4": {"v1": TCP - 3, "v3": 8},
        }
        finder = finder_class(digraph)
        return run_lawler_TCP2(finder, dist)

    class MyBSOracle(OracleBS):
        def assess_bs(self, gamma):
            return not has_negative_cycle(gamma, dist)

    omega = MyBSOracle()
    options = Options()
    options.max_iters = MAX_ITERS
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (5.0, 10.0), options)
    print(opt, num_iter)
    assert opt == approx(6.6)
    assert num_iter <= 50


@pytest.mark.parametrize("finder_class", finders)
def test_maximize_slack(finder_class):
    TCP = 7.5
    digraph = {
        "v0": {"v3": TCP - 6, "v2": 6},
        "v1": {"v2": TCP - 9, "v4": 3},
        "v2": {"v0": TCP - 7, "v1": 6},
        "v3": {"v4": TCP - 8, "v0": 6},
        "v4": {"v1": TCP - 3, "v3": 8},
    }
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}

    def has_negative_cycle_EVEN(beta, dist):
        finder = finder_class(digraph)
        return run_lawler_even2(finder, dist, beta)

    class MyBSOracle2(OracleBS):
        def assess_bs(self, gamma):
            ic(gamma)
            return has_negative_cycle_EVEN(gamma, dist)

    omega = MyBSOracle2()
    options = Options()
    options.max_iters = MAX_ITERS
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (0.0, 10.0), options)
    print(opt, num_iter)
    assert opt == approx(0.9)
    assert num_iter <= 50


@pytest.mark.parametrize("finder_class", finders)
def test_maximize_effective_slack(finder_class):
    TCP = 7.5
    digraph = {
        "v0": {"v3": {"cost": TCP - 6, "time": 3.1}, "v2": {"cost": 6, "time": 1.5}},
        "v1": {"v2": {"cost": TCP - 9, "time": 4.1}, "v4": {"cost": 3, "time": 1.0}},
        "v2": {"v0": {"cost": TCP - 7, "time": 3.1}, "v1": {"cost": 6, "time": 2.5}},
        "v3": {"v4": {"cost": TCP - 8, "time": 4.1}, "v0": {"cost": 6, "time": 2.5}},
        "v4": {"v1": {"cost": TCP - 3, "time": 1.1}, "v3": {"cost": 8, "time": 1.5}},
    }
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}

    def has_negative_cycle_PROP(beta, dist):
        finder = finder_class(digraph)
        return run_lawler_prop2(finder, dist, beta)

    class MyBSOracle3(OracleBS):
        def assess_bs(self, gamma):
            return has_negative_cycle_PROP(gamma, dist)

    omega = MyBSOracle3()
    options = Options()
    options.tolerance = TOLERANCE
    options.max_iters = MAX_ITERS
    opt, num_iter = bsearch(omega, (0.0, 10.0), options)
    print(opt, num_iter)
    assert opt == approx(0.290322580645161)
    assert num_iter <= 50
