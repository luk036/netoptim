"""Multi-parameter clock-skew scheduling oracle.

Wraps Howard's negative-cycle finder as a separation oracle for the
two-parameter (clock period, yield) ratio problem, driven by the ellipsoid
method (:func:`ellalgo.cutting_plane.cutting_plane_optim`).
"""

from typing import Any, Dict, Optional, Tuple

import numpy as np
from digraphx.neg_cycle import NegCycleFinder
from ellalgo.ell_typing import OracleOptim

from ._typing import Cut

Arr = np.ndarray
"""A two-element iterate ``(TCP, beta)``."""


class ClockScheduleOracle(OracleOptim[Arr]):
    """Oracle for minimum-period / maximum-yield clock skew scheduling.

    Solves ``min TCP / beta`` subject to the timing constraint graph being
    feasible at period ``TCP`` and yield ``beta``.  The iterate is
    ``x = (TCP, beta)``; the timing constraint graph is given as an
    adjacency mapping whose edges carry ``{"type": "s"|"h", "delay": d}``.
    A negative cycle, if any, supplies the separating cutting plane.
    """

    def __init__(self, gra: Any, dist: Dict[Any, float]) -> None:
        """Initialize the oracle.

        Args:
            gra: The timing constraint graph (adjacency mapping).
            dist: Initial node potentials, mutated in place by the
                negative-cycle search.
        """
        self._finder: NegCycleFinder[Any, Any, float] = NegCycleFinder(gra)
        self._dist = dist

    def assess_optim(self, xc: Arr, gamma: float) -> Tuple[Cut, Optional[float]]:
        """Assess optimality and return a cutting plane if suboptimal.

        Args:
            xc: The current iterate ``(TCP, beta)``.
            gamma: Best-so-far value of ``TCP / beta``.

        Returns:
            ``(cut, value)`` where ``value`` is ``TCP / beta`` at optimality,
            or ``None`` if a cutting plane was produced.
        """
        TCP, beta = xc
        if TCP < 0.0:
            return (np.array([-1.0, 0.0]), -TCP), None
        if (fj := TCP - gamma * beta) > 0.0:
            return (np.array([1.0, -gamma]), fj), None

        def get_weight(e: Dict[str, Any]) -> float:
            return TCP - e["delay"] - beta if e["type"] == "s" else e["delay"] - beta

        for cycle in self._finder.howard(self._dist, get_weight):
            f = -sum(get_weight(e) for e in cycle)
            g = np.array(
                [-sum(1.0 if e["type"] == "s" else 0.0 for e in cycle), len(cycle)]
            )
            return (g, f), None

        return (np.array([1.0, -1.0]), 0.0), TCP / beta
