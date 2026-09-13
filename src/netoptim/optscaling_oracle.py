from typing import Any, Callable, Optional, Tuple

import numpy as np
from ellalgo.ell_typing import OracleOptim

from ._typing import Cut
from .network_oracle import NetworkOracle

Arr = np.ndarray
"""A NumPy array type alias for array operations in the optimization."""


class OptScalingOracle(OracleOptim[Arr]):
    """Oracle for Optimal Matrix Scaling

    This example is taken from[Orlin and Rothblum, 1985]

    .. svgbob::

        (u_i) <------ w_ji ------ (u_j)
              ------> w_ij ------

    |    min     π/ψ
    |    s.t.    ψ ≤ u[i] * ``|a_ij|`` * u[j]^{−1} ≤ π,
    |            ∀ (i,j) ∈ E,
    |            π, ψ, utx, positive
    """

    class Ratio:
        """Inner class for computing ratio constraints in matrix scaling.

        This class evaluates the constraint ψ ≤ u[i] * |a_ij| * u[j]^{-1} ≤ π
        by computing the minimum of two differences in logarithmic scale.
        """

        def __init__(self, gra: Any, get_cost: Any) -> None:
            """Initialize the Ratio evaluator.

            Args:
                gra: The graph structure representing the matrix.
                get_cost: A callable that returns the pair (a_ij, a_ji) of
                    absolute matrix entries for a given edge.
            """
            self._gra = gra
            self._get_cost = get_cost

        def eval(self, edge: Any, x: Arr) -> float:
            """Evaluate the ratio constraint for an edge.

            Computes min(π - a_ji, a_ij - ψ) where x = (π, ψ) in log scale.
            A positive result indicates the constraint is satisfied.

            Args:
                edge: The edge (i, j) to evaluate.
                x: The current iterate (π, ψ) in logarithmic scale.

            Returns:
                The minimum of the two ratio differences.
            """
            aij, aji = self._get_cost(edge)
            return min(x[0] - aji, aij - x[1])

        def make_weight_fn(self, x: Arr) -> Callable[[Any], float]:
            """Return a weight evaluator with the iterate's scalars bound once.

            :class:`~netoptim.network_oracle.NetworkOracle` calls this once per
            assessment so the per-edge hot loop avoids repeatedly indexing the
            NumPy iterate ``x``.

            Args:
                x: The current iterate (π, ψ) in logarithmic scale.

            Returns:
                A callable mapping an edge to its ratio weight.
            """
            x0 = float(x[0])
            x1 = float(x[1])
            get_cost = self._get_cost

            def weight(edge: Any) -> float:
                aij, aji = get_cost(edge)
                d0 = x0 - aji
                d1 = aij - x1
                return d0 if d0 < d1 else d1

            return weight

        def grad(self, edge: Any, x: Arr) -> Arr:
            """Compute the subgradient of the ratio constraint.

            Returns a subgradient vector indicating which bound is active:
            - [1.0, 0.0] if the upper bound (π) is active
            - [0.0, -1.0] if the lower bound (ψ) is active

            Args:
                edge: The edge (i, j) to evaluate.
                x: The current iterate (π, ψ) in logarithmic scale.

            Returns:
                A 2-element NumPy array representing the subgradient.
            """
            aij, aji = self._get_cost(edge)
            if x[0] - aji < aij - x[1]:
                return np.array([1.0, 0.0])
            return np.array([0.0, -1.0])

        def update(self, t: Any) -> None:
            """No-op hook: matrix scaling has no best-so-far parameter."""
            pass

    def __init__(self, gra: Any, utx: Any, get_cost: Any) -> None:
        """Construct a new OptScalingOracle instance.

        Args:
            gra: The graph structure representing the matrix to be scaled.
            utx: Initial node potentials (one per node), typically zeros.
            get_cost: A callable ``get_cost(edge) -> (a_ij, a_ji)`` that
                returns the pair of absolute matrix entries for an edge.

        Examples:
            >>> from mywheel.map_adapter import MapAdapter
            >>> gra = MapAdapter([[0, 1], [1, 0]])
            >>> utx = [0.0, 0.0]
            >>> def get_cost(edge):
            ...     return 1.0, 1.0
            >>> oracle = OptScalingOracle(gra, utx, get_cost)
            >>> isinstance(oracle._network, NetworkOracle)
            True
        """
        self._network = NetworkOracle(gra, utx, self.Ratio(gra, get_cost))

    def assess_optim(self, xc: Arr, gamma: float) -> Tuple[Cut, Optional[float]]:
        """Assess optimality and return a cutting plane if suboptimal.

        Implements the oracle interface required by ``cutting_plane_optim()``.
        First checks feasibility via the network oracle; if feasible, checks
        whether the current objective value can be improved.

        Args:
            xc: The current iterate (π, ψ) in logarithmic scale.
            gamma: The best-so-far optimal value.

        Returns:
            A tuple ``(cut, value)`` where ``cut`` is a ``(gradient, intercept)``
            pair and ``value`` is either the objective value (if optimal) or
            ``None`` (if a cutting plane was generated).

        Examples:
            >>> from mywheel.map_adapter import MapAdapter
            >>> gra = MapAdapter([{}, {0: (1.0, 1.0)}])
            >>> utx = [0.0, 0.0]
            >>> def get_cost(edge):
            ...     return 1.0, 1.0
            >>> oracle = OptScalingOracle(gra, utx, get_cost)
            >>> x = np.array([0.0, 0.0])
            >>> t = 0.0
            >>> cut, t1 = oracle.assess_optim(x, t)
            >>> cut[0]
            array([ 1., -1.])
            >>> cut[1]
            0.0
            >>> import numpy as np
            >>> bool(np.isclose(t1, 0.0))
            True

            >>> x = np.array([1.0, 0.0])
            >>> t = 0.0
            >>> cut, t1 = oracle.assess_optim(x, t)
            >>> cut[0]
            array([ 1., -1.])

        See also:
            cutting_plane_optim
        """
        if (cut := self._network.assess_feas(xc)) is not None:
            return cut, None

        s = xc[0] - xc[1]
        g = np.array([1.0, -1.0])
        if (fj := s - gamma) > 0.0:
            return (g, fj), None

        return (g, 0.0), s
