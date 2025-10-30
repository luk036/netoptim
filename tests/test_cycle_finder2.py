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


@pytest.fixture
def dist():
    return {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}


def run_lawler(finder, dist, weight_fn):
    """
    Checks if a negative cycle exists in a graph using the Lawler-Howard algorithm.

    Args:
        finder: An instance of a cycle finder algorithm (e.g., NegCycleFinder).
        dist (dict): A dictionary representing the distances or potentials of the nodes.
        weight_fn (callable): A function that takes an edge and returns its weight.

    Returns:
        bool: True if a negative cycle is found, False otherwise.
    """
    if isinstance(finder, NegCycleFinderQ):
        for _ in finder.howard_succ(dist, weight_fn, lambda _, __: True):
            return True
    else:
        for _ in finder.howard(dist, weight_fn):
            return True
    return False


def run_bsearch(omega, interval, options):
    """
    Runs a binary search algorithm to find the optimal value.

    Args:
        omega (OracleBS): An oracle object for the binary search.
        interval (tuple): A tuple representing the search interval (e.g., (min_val, max_val)).
        options (Options): An object containing configuration options for the search.

    Returns:
        tuple: A tuple containing the optimal value and the number of iterations.
    """
    opt, num_iter = bsearch(omega, interval, options)
    print(opt, num_iter)
    return opt, num_iter


class MyBSOracle(OracleBS):
    def __init__(self, has_negative_cycle, dist, callback=None):
        self.has_negative_cycle = has_negative_cycle
        self.dist = dist
        self.callback = callback

    def assess_bs(self, gamma):
        if self.callback:
            self.callback(gamma)
        return self.has_negative_cycle(gamma, self.dist)


@pytest.mark.parametrize("finder_class", finders)
def test_minimize_TCP2(finder_class, dist):
    def has_negative_cycle(TCP, dist):
        """Creates a test graph for timing tests."""
        digraph = {
            "v0": {"v3": TCP - 6, "v2": TCP - 7},
            "v1": {"v2": TCP - 9, "v4": 3},
            "v2": {"v0": 6, "v1": 6, "v3": TCP - 6},
            "v3": {"v4": TCP - 8, "v0": 6, "v2": 6},
            "v4": {"v1": TCP - 3, "v3": 8},
        }
        finder = finder_class(digraph)
        return run_lawler(finder, dist, lambda edge: edge)

    omega = MyBSOracle(lambda g, d: not has_negative_cycle(g, d), dist)
    options = Options()
    options.max_iters = MAX_ITERS
    options.tolerance = TOLERANCE
    opt, num_iter = run_bsearch(omega, (5.0, 10.0), options)
    assert opt == approx(6.5)
    assert num_iter <= 50


@pytest.mark.parametrize("finder_class", finders)
def test_maximize_slack(finder_class, dist):
    TCP = 7.5
    digraph = {
        "v0": {"v3": TCP - 6, "v2": TCP - 7},
        "v1": {"v2": TCP - 9, "v4": 3},
        "v2": {"v0": 6, "v1": 6, "v3": TCP - 6},
        "v3": {"v4": TCP - 8, "v0": 6, "v2": 6},
        "v4": {"v1": TCP - 3, "v3": 8},
    }

    def has_negative_cycle_EVEN(beta, dist):
        finder = finder_class(digraph)
        return run_lawler(finder, dist, lambda edge: edge - beta)

    omega = MyBSOracle(has_negative_cycle_EVEN, dist, callback=ic)
    options = Options()
    options.max_iters = MAX_ITERS
    options.tolerance = TOLERANCE
    opt, num_iter = run_bsearch(omega, (0.0, 10.0), options)
    assert opt == approx(1.0)
    assert num_iter <= 50


@pytest.mark.parametrize("finder_class", finders)
def test_maximize_effective_slack(finder_class, dist):
    TCP = 7.5
    digraph = {
        "v0": {
            "v3": {"cost": TCP - 6, "time": 3.1},
            "v2": {"cost": TCP - 7, "time": 1.5},
        },
        "v1": {"v2": {"cost": TCP - 9, "time": 4.1}, "v4": {"cost": 3, "time": 1.0}},
        "v2": {
            "v0": {"cost": 6, "time": 3.1},
            "v1": {"cost": 6, "time": 2.5},
            "v3": {"cost": TCP - 6, "time": 3.1},
        },
        "v3": {
            "v4": {"cost": TCP - 8, "time": 4.1},
            "v0": {"cost": 6, "time": 2.5},
            "v2": {"cost": 6, "time": 2.5},
        },
        "v4": {"v1": {"cost": TCP - 3, "time": 1.1}, "v3": {"cost": 8, "time": 1.5}},
    }

    def has_negative_cycle_PROP(beta, dist):
        finder = finder_class(digraph)
        return run_lawler(finder, dist, lambda edge: edge["cost"] - beta * edge["time"])

    omega = MyBSOracle(has_negative_cycle_PROP, dist)
    options = Options()
    options.tolerance = TOLERANCE
    options.max_iters = MAX_ITERS
    opt, num_iter = run_bsearch(omega, (0.0, 10.0), options)
    assert opt == approx(0.32258064516129037)
    assert num_iter <= 50
