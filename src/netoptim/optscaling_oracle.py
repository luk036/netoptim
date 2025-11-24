from typing import Optional, Tuple

import numpy as np
from ellalgo.ell_typing import OracleOptim

from .network_oracle import NetworkOracle

Arr = np.ndarray
Cut = Tuple[Arr, float]


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
        def __init__(self, gra, get_cost):
            """[summary]

            Arguments:
                gra ([type]): [description]
            """
            self._gra = gra
            self._get_cost = get_cost

        def eval(self, edge, x: Arr) -> float:
            """[summary]

            Arguments:
                edge ([type]): [description]
                x (Arr): (π, ψ) in log scale

            Returns:
                float: function evaluation
            """
            aij, aji = self._get_cost(edge)
            return min(x[0] - aji, aij - x[1])

        def grad(self, edge, x: Arr) -> Arr:
            """[summary]

            Arguments:
                edge ([type]): [description]
                x (Arr): (π, ψ) in log scale

            Returns:
                [type]: [description]
            """
            aij, aji = self._get_cost(edge)
            if x[0] - aji < aij - x[1]:
                return np.array([1.0, 0.0])
            return np.array([0.0, -1.0])

    def __init__(self, gra, utx, get_cost):
        """Construct a new optscaling oracle object

        Arguments:
            gra ([type]): [description]

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
        """
        Make object callable for cutting_plane_optim()

        Arguments:
            x (Arr): (π, ψ) in log scale
            t (float): the best-so-far optimal value

        Returns:
            Tuple[Cut, Optional[float]]

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
