from typing import Any, Optional, Tuple

from digraphx.neg_cycle import NegCycleFinder

Cut = Tuple[Any, float]


class NetworkOracle:
    """Oracle for Parametric Network Problem:

    The `NetworkOracle` class represents an oracle for solving a parametric network problem, where the
    goal is to find values for variables `x` and `u` that satisfy certain constraints.

    |   find    x, u
    |   s.t.    u[j] − u[i] ≤ h(edge, x)
    |           ∀ edge(i, j) ∈ E
    """

    def __init__(self, gra, u, h):
        """
        The function initializes an object with a directed graph, a list or dictionary, and a function for
        evaluation and gradient.

        :param gra: The parameter `gra` is a directed graph represented by a tuple `(Node, E)`. `Node`
        represents the set of nodes in the graph, and `E` represents the set of edges in the graph
        :param u: The `u` parameter is either a list or a dictionary. It represents the initial values
        of the variables in the optimization problem. The specific meaning of these variables depends on the
        context of the optimization problem being solved
        :param h: The parameter `h` is a function that is used for evaluation and gradient calculations. It
        takes in some input and returns the evaluation value and gradient of that input
        """
        self._gra = gra
        self._potential = u
        self._h = h
        self._ncf = NegCycleFinder(gra)

    def update(self, t):
        """[summary]

        Arguments:
            t (float): the best-so-far optimal value
        """
        self._h.update(t)

    def assess_feas(self, x) -> Optional[Cut]:
        """Make object callable for cutting_plane_feas()

        Arguments:
            x ([type]): [description]

        Returns:
            Optional[Cut]: [description]
        """

        def get_weight(edge):
            """[summary]

            Arguments:
                edge ([type]): [description]

            Returns:
                Any: [description]
            """
            return self._h.eval(edge, x)

        for cycle in self._ncf.howard(self._potential, get_weight):
            f = -sum(self._h.eval(edge, x) for edge in cycle)
            g = -sum(self._h.grad(edge, x) for edge in cycle)
            # TODO: choose the minumum cycle
            return g, f  # use the first cycle only

        return None
