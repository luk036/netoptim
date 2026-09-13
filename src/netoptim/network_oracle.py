from typing import Any, Callable, Dict, Optional, Tuple, Union

from digraphx.neg_cycle import NegCycleFinder
from ellalgo.ell_typing import OracleFeas

from ._typing import Cut, EdgeOracle

Graph = Dict[Any, Dict[Any, Union[Dict[str, Any], Tuple[Any, Any]]]]
"""A directed graph represented as an adjacency dictionary.

The outer dict maps each node to a dict of its neighbors.
Each neighbor maps to either a dict of edge attributes (e.g., {'w': weight})
or a tuple of (source, target) edge information.
"""


def _bound_eval(oracle: EdgeOracle, x: Any) -> Callable[[Any], float]:
    def weight(edge: Any) -> float:
        return oracle.eval(edge, x)

    return weight


class NetworkOracle(OracleFeas[Any]):
    """Oracle for Parametric Network Problem:

    The `NetworkOracle` class represents an oracle for solving a parametric network problem, where the
    goal is to find values for variables `x` and `u` that satisfy certain constraints.

    .. svgbob::

        (u_i) ------ w(i,j) ------> (u_j)

        u_j - u_i <= w(i,j)

    |   find    x, u
    |   s.t.    u[j] − u[i] ≤ oracle(edge, x)
    |           ∀ edge(i, j) ∈ E

    Examples:
        >>> from unittest.mock import Mock
        >>> gra = {
        ...     "v1": {"v2": {"w": 3}, "v3": {"w": 4}},
        ...     "v2": {"v1": {"w": -2}, "v3": {"w": 1}},
        ...     "v3": {"v1": {"w": -3}, "v2": {"w": -2}},
        ... }
        >>> u = {"v1": 0.0, "v2": 0.0, "v3": 0.0}
        >>> oracle = Mock()
        >>> oracle.eval.side_effect = lambda e, x: e["w"] - x
        >>> oracle.grad.side_effect = lambda e, x: -1
        >>> network = NetworkOracle(gra, u, oracle)
        >>> network.assess_feas(1)
        (2, 3)
    """

    def __init__(self, gra: Graph, u: Dict[Any, float], oracle: EdgeOracle) -> None:
        """
        Initialize the network oracle with a graph, node potentials, and an edge oracle.

        :param gra: The directed graph represented as an adjacency dictionary
            mapping each node to its neighbors and edge attributes.
        :param u: The initial node potentials, a dictionary mapping each node
            to its starting potential value.
        :param oracle: The oracle object that provides `eval(edge, x)` and
            `grad(edge, x)` methods for evaluating edge weights and their
            subgradients at a given iterate x.
        """
        self._gra = gra
        self._potential = u
        self._oracle = oracle
        self._ncf: NegCycleFinder[Any, Any, float] = NegCycleFinder(gra)

    def update(self, t: float) -> None:
        """Update the oracle with the best-so-far optimal value.

        This method notifies the underlying oracle about the current best
        feasible solution value, which may be used to refine cutting planes.

        Args:
            t: The best-so-far optimal value to update the oracle with.
        """
        self._oracle.update(t)

    def assess_feas(self, x: Any) -> Optional[Cut]:
        """Assess feasibility and generate a cutting plane if infeasible.

        This method implements the feasibility oracle for the parametric
        network problem. It searches for negative cycles in the graph
        using Howard's algorithm. If a negative cycle exists, it returns
        a cutting plane (gradient, intercept) to cut off the infeasible point.

        Args:
            x: The current iterate value to assess for feasibility.

        Returns:
            A Cut tuple (gradient, intercept) if the point is infeasible
            (negative cycle exists), or None if feasible.
        """

        oracle = self._oracle
        # type-level check so unittest.mock.Mock auto-attributes are not mistaken
        # for the optional hook
        if hasattr(type(oracle), "make_weight_fn"):
            get_weight = getattr(oracle, "make_weight_fn")(x)
        else:
            get_weight = _bound_eval(oracle, x)

        for cycle in self._ncf.howard(self._potential, get_weight):
            f = -sum(get_weight(edge) for edge in cycle)
            g = -sum(oracle.grad(edge, x) for edge in cycle)
            # TODO: choose the minumum cycle
            return g, f  # use the first cycle only

        return None
