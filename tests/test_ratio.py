from typing import Any, Dict, Tuple, Optional

from digraphx.neg_cycle import NegCycleFinder

# from ellalgo.ell_config import Options
from ellalgo.ell_typing import OracleOptim

# from pytest import approx
import numpy as np
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell

MAX_ITERS = 100
TOLERANCE = 1e-7

Finders = [NegCycleFinder]
Arr = np.ndarray
Cut = Tuple[Arr, float]


class MyOracle(OracleOptim[np.ndarray]):
    def __init__(
        self,
        dist: Dict[str, int],
        digraph,
    ):
        self.dist = dist
        self.finder = NegCycleFinder(digraph)

    def assess_optim(self, xc: np.ndarray, gamma: float) -> Tuple[Cut, Optional[float]]:
        TCP, beta = xc
        if TCP < 0.0:
            return (np.array([-1.0, 0.0]), -TCP), None
        if (fj := TCP - gamma * beta) > 0:
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
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
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
    ellip = Ell(100, xinit)
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    omega = MyOracle(dist, digraph)
    xbest, ratio, _ = cutting_plane_optim(omega, ellip, float("inf"))
    print(xbest)
    print(ratio)
    assert xbest is not None
