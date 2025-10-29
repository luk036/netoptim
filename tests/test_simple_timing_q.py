from digraphx.neg_cycle_q import NegCycleFinderQ
from pytest import approx
from ellalgo.cutting_plane import bsearch
from ellalgo.ell_typing import OracleBS
from ellalgo.ell_config import Options

MAX_ITERS = 2000
TOLERANCE = 1e-14


def _always_ok(d, v):
    return True


def has_negative_cycle(TCP, dist):
    """Creates a test graph for timing tests."""
    digraph = {
        "v1": {"v2": TCP - 2, "v3": 1.5},
        "v2": {"v3": TCP - 3, "v1": 2},
        "v3": {"v1": TCP - 4, "v2": 3},
    }
    finder = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, lambda edge: edge, _always_ok):
        return True
    return False


class MyBSOracle(OracleBS):
    def __init__(self, dist):
        self.dist = dist

    def assess_bs(self, gamma):
        return not has_negative_cycle(gamma, self.dist)


def test_minimize_TCP():
    dist = {"v1": 0, "v2": 0, "v3": 0}
    omega = MyBSOracle(dist)
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (2.0, 4.0), options)
    print(opt, num_iter)
    assert opt == approx(3.0)
    assert num_iter <= 50


def has_negative_cycle_EVEN(beta, dist):
    TCP = 4.5
    digraph = {
        "v1": {"v2": TCP - 2 - beta, "v3": 1.5 - beta},
        "v2": {"v3": TCP - 3 - beta, "v1": 2 - beta},
        "v3": {"v1": TCP - 4 - beta, "v2": 3 - beta},
    }
    finder = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, lambda edge: edge, _always_ok):
        return True
    return False


class MyBSOracle2(OracleBS):
    def __init__(self, dist):
        self.dist = dist

    def assess_bs(self, gamma):
        return has_negative_cycle_EVEN(gamma, self.dist)


def test_maximize_slack():
    dist = {"v1": 0, "v2": 0, "v3": 0}
    omega = MyBSOracle2(dist)
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (0, 10.0), options)
    print(opt, num_iter)
    assert opt == approx(1.0)
    assert num_iter <= 50


def has_negative_cycle_PROP(beta, dist):
    """Creates a test graph for timing tests."""
    TCP = 4.5
    digraph = {
        "v1": {"v2": TCP - 2 - beta * 3.1, "v3": 1.5 - beta * 0.7},
        "v2": {"v3": TCP - 3 - beta * 4.1, "v1": 2 - beta * 2.2},
        "v3": {"v1": TCP - 4 - beta * 5.1, "v2": 3 - beta * 1.5},
    }
    finder = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, lambda edge: edge, _always_ok):
        return True
    return False


class MyBSOracle3(OracleBS):
    def __init__(self, dist):
        self.dist = dist

    def assess_bs(self, gamma):
        return has_negative_cycle_PROP(gamma, self.dist)


def test_maximize_effective_slack():
    dist = {"v1": 0, "v2": 0, "v3": 0}
    omega = MyBSOracle3(dist)
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, (0, 10.0), options)
    print(opt, num_iter)
    assert opt == approx(0.3448275862069039)
    assert num_iter <= 50
