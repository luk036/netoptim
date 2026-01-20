from typing import Any, Dict, Optional, Tuple

from digraphx.neg_cycle import NegCycleFinder

Cut = Tuple[Any, float]
Graph = Dict[Any, Dict[Any, Dict[str, Any]]]


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

    def __init__(self, gra: Graph, u: Dict[Any, float], oracle: Any) -> None:
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
        """[summary]

        Arguments:
            t (float): the best-so-far optimal value
        """
        self._oracle.update(t)

    def assess_feas(self, x: float) -> Optional[Cut]:
        """Make object callable for cutting_plane_feas()

        Arguments:
            x (float): [description]

        Returns:
            Optional[Cut]: [description]
        """

        def get_weight(edge):
            """[summary]

            Arguments:
                edge ([type]): [description]

            Returns:
                Iterator: [description]
            """
            return self._oracle.eval(edge, x)

        for cycle in self._ncf.howard(self._potential, get_weight):
            f = -sum(self._oracle.eval(edge, x) for edge in cycle)
            g = -sum(self._oracle.grad(edge, x) for edge in cycle)
            # TODO: choose the minumum cycle
            return g, f  # use the first cycle only

        return None
