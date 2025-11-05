from typing import Any, Dict, Tuple, Optional

from digraphx.neg_cycle import NegCycleFinder
from pytest import approx

from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell
from ellalgo.ell_typing import OracleOptim
import numpy as np

Arr = np.ndarray
Cut = Tuple[Arr, float]
Digraph = Dict[str, Dict[str, Dict[str, Any]]]


class MyOracle(OracleOptim[Arr]):
    """Oracle for the ratio test problem."""

    def __init__(self, digraph: Digraph, dist: Dict[str, int]):
        """Initialize the oracle.

        Args:
            digraph (Digraph): The directed graph.
            dist (Dict[str, int]): The distance dictionary.
        """
        self.finder = NegCycleFinder(digraph)
        self.dist = dist

    def assess_optim(self, xc: Arr, gamma: float) -> Tuple[Cut, Optional[float]]:
        """Assess the optimality of the solution.

        Args:
            xc (Arr): The solution to assess.
            gamma (float): The current best solution.

        Returns:
            Tuple[Cut, Optional[float]]: A tuple containing the cut and the objective value.
        """
        TCP, beta = xc
        if TCP < 0.0:
            return (np.array([-1.0, 0.0]), -TCP), None
        if (fj := TCP - gamma * beta) > 0.0:
            return (np.array([1.0, -gamma]), fj), None

        def calc_weight(e):
            return TCP - e["delay"] - beta if e["type"] == "s" else e["delay"] - beta

        for cycle in self.finder.howard(self.dist, calc_weight):
            f = -sum(calc_weight(e) for e in cycle)
            g = np.array(
                [-sum(1.0 if e["type"] == "s" else 0.0 for e in cycle), len(cycle)]
            )
            return (g, f), None  # use the first cycle only

        return (np.array([1.0, -1.0]), 0.0), TCP / beta


def test_minimize_ratio():
    """Test the minimization of the ratio."""
    digraph: Digraph = {
        "v0": {"v3": {"type": "s", "delay": 6}, "v2": {"type": "s", "delay": 7}},
        "v1": {"v2": {"type": "s", "delay": 9}, "v4": {"type": "h", "delay": 3}},
        "v2": {
            "v0": {"type": "h", "delay": 6},
            "v1": {"type": "h", "delay": 6},
            "v3": {"type": "s", "delay": 6},
        },
        "v3": {
            "v4": {"type": "s", "delay": 8},
            "v0": {"type": "h", "delay": 6},
            "v2": {"type": "h", "delay": 6},
        },
        "v4": {"v1": {"type": "s", "delay": 3}, "v3": {"type": "h", "delay": 8}},
    }

    xinit = np.array([7.5, 1.0])
    ellip = Ell(100.0, xinit)
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    omega = MyOracle(digraph, dist)
    xbest, ratio, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None
    assert ratio is not None
    assert ratio == approx(3.040717067415985)
