from typing import Any, Dict, Optional, Tuple, Union

from digraphx.neg_cycle import NegCycleFinder

Cut = Tuple[Any, float]
"""A cutting plane represented as a tuple of (gradient, intercept).

The gradient is typically a vector representing the subgradient of the
objective function, and the intercept is the constant term in the
linear cut.
"""

Graph = Dict[Any, Dict[Any, Union[Dict[str, Any], Tuple[Any, Any]]]]
"""A directed graph represented as an adjacency dictionary.

The outer dict maps each node to a dict of its neighbors.
Each neighbor maps to either a dict of edge attributes (e.g., {'w': weight})
or a tuple of (source, target) edge information.
"""


class NetworkOracle:
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
        >>> u = {"v1": 0, "v2": 0, "v3": 0}
        >>> oracle = Mock()
        >>> oracle.eval.side_effect = lambda e, x: e["w"] - x
        >>> oracle.grad.side_effect = lambda e, x: -1
        >>> network = NetworkOracle(gra, u, oracle)
        >>> network.assess_feas(1)
        (2, 3)
    """

    def __init__(self, gra: Graph, u: Dict[Any, int], oracle: Any) -> None:
        """
        The function initializes an object with a directed graph, a list or dictionary, and a function for
        evaluation and gradient.

        :param gra: The parameter `gra` is a directed graph represented by a tuple `(Node, E)`. `Node`
        represents the set of nodes in the graph, and `E` represents the set of edges in the graph
        :param u: The `u` parameter is either a list or a dictionary. It represents the initial values
        of the variables in the optimization problem. The specific meaning of these variables depends on the
        context of the optimization problem being solved
        :param oracle: The parameter `oracle` is a function that is used for evaluation and gradient calculations. It
        takes in some input and returns the evaluation value and gradient of that input
        """
        self._gra = gra
        self._potential = u
        self._oracle = oracle
        self._ncf = NegCycleFinder(gra)

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

        def get_weight(edge):
            """Compute the weight of an edge given the current iterate.

            Args:
                edge: The edge (i, j) to compute weight for.

            Returns:
                The oracle evaluation value for the edge at iterate x.
            """
            return self._oracle.eval(edge, x)

        for cycle in self._ncf.howard(self._potential, get_weight):
            f = -sum(self._oracle.eval(edge, x) for edge in cycle)
            g = -sum(self._oracle.grad(edge, x) for edge in cycle)
            # TODO: choose the minumum cycle
            return g, f  # use the first cycle only

        return None
