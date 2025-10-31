import pytest
from digraphx.neg_cycle import NegCycleFinder
from digraphx.neg_cycle_q import NegCycleFinderQ
from pytest import approx
from ellalgo.cutting_plane import bsearch
from ellalgo.ell_typing import OracleBS
from ellalgo.ell_config import Options

MAX_ITERS = 2000
TOLERANCE = 1e-14

finders = [NegCycleFinder, NegCycleFinderQ]


def run_lawler_TCP(finder, dist, TCP):
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


def run_lawler_even(finder, dist, beta):
    if isinstance(finder, NegCycleFinderQ):
        for _ in finder.howard_succ(dist, lambda edge: edge - beta, lambda _, __: True):
            return True
    else:
        for _ in finder.howard(dist, lambda edge: edge - beta):
            return True
    return False


def run_lawler_prop(finder, dist, beta):
    if isinstance(finder, NegCycleFinderQ):
        for _ in finder.howard_succ(
            dist, lambda edge: edge["cost"] - beta * edge["time"], lambda _, __: True
        ):
            return True
    else:
        for _ in finder.howard(dist, lambda edge: edge["cost"] - beta * edge["time"]):
            return True
    return False


@pytest.mark.parametrize("finder_class", finders)
def test_minimize_TCP(finder_class):
    dist = {"v1": 0, "v2": 0, "v3": 0}
    digraph = {
        "v1": {"v2": {"type": "s", "delay": 2}, "v3": {"type": "h", "delay": 1.5}},
        "v2": {"v3": {"type": "s", "delay": 3}, "v1": {"type": "h", "delay": 2.0}},
        "v3": {"v1": {"type": "s", "delay": 4}, "v2": {"type": "h", "delay": 3.0}},
    }

    def has_negative_cycle(TCP, dist):
        finder = finder_class(digraph)
        return run_lawler_TCP(finder, dist, TCP)

    class MyBSOracle(OracleBS):
        def assess_bs(self, gamma):
            return not has_negative_cycle(gamma, dist)

    omega = MyBSOracle()
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (2.0, 4.0), options)
    print(opt, num_iter)
    assert opt == approx(3.0)
    assert num_iter <= 50


@pytest.mark.parametrize("finder_class", finders)
def test_maximize_slack(finder_class):
    dist = {"v1": 0, "v2": 0, "v3": 0}
    TCP = 4.5
    digraph = {
        "v1": {"v2": TCP - 2, "v3": 1.5},
        "v2": {"v3": TCP - 3, "v1": 2.0},
        "v3": {"v1": TCP - 4, "v2": 3.0},
    }

    def has_negative_cycle_EVEN(beta, dist):
        finder = finder_class(digraph)
        return run_lawler_even(finder, dist, beta)

    class MyBSOracle2(OracleBS):
        def assess_bs(self, gamma):
            return has_negative_cycle_EVEN(gamma, dist)

    omega = MyBSOracle2()
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (0.0, 10.0), options)
    print(opt, num_iter)
    assert opt == approx(1.0)
    assert num_iter <= 50


@pytest.mark.parametrize("finder_class", finders)
def test_maximize_effective_slack(finder_class):
    dist = {"v1": 0, "v2": 0, "v3": 0}
    TCP = 4.5
    digraph = {
        "v1": {"v2": {"cost": TCP - 2, "time": 3.1}, "v3": {"cost": 1.5, "time": 0.7}},
        "v2": {"v3": {"cost": TCP - 3, "time": 4.1}, "v1": {"cost": 2.0, "time": 2.2}},
        "v3": {"v1": {"cost": TCP - 4, "time": 5.1}, "v2": {"cost": 3.0, "time": 1.5}},
    }

    def has_negative_cycle_PROP(beta, dist):
        finder = finder_class(digraph)
        return run_lawler_prop(finder, dist, beta)

    class MyBSOracle3(OracleBS):
        def assess_bs(self, gamma):
            return has_negative_cycle_PROP(gamma, dist)

    omega = MyBSOracle3()
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (0.0, 10.0), options)
    print(opt, num_iter)
    assert opt == approx(0.3448275862069039)
    assert num_iter <= 50
