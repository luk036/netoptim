from .parametric import MaxParametricSolver, ParametricAPI, R, V, Cycle
from typing import Tuple, Any, Generic
from typing import MutableMapping, Mapping, TypeVar
from fractions import Fraction

D = TypeVar("D", int, float, Fraction)  # Comparable Ring


def set_default(gra: Mapping[V, Mapping[V, Any]], weight: str, value: D) -> None:
    """_summary_

    Args:
        gra (Mapping[V, Mapping[V, Any]]): _description_
        weight (str): _description_
        value (Any): _description_
    """
    for utx in gra:
        for vtx in gra[utx]:
            if gra[utx][vtx].get(weight, None) is None:
                gra[utx][vtx][weight] = value


class CycleRatioAPI(ParametricAPI[V, R]):
    def __init__(self, gra: Mapping[V, Mapping[V, Any]], T: type) -> None:
        """_summary_

        Args:
            gra (Mapping[V, Mapping[V, Any]]): _description_
            T (type): _description_
        """
        self.gra = gra
        self.T = T

    def distance(self, ratio: R, edge: Tuple[V, V]) -> R:
        """[summary]

        Arguments:
            ratio ([type]): [description]
            edge ([type]): [description]

        Returns:
            [type]: [description]
        """
        utx, vtx = edge
        return self.gra[utx][vtx]["cost"] - ratio * self.gra[utx][vtx]["time"]

    def zero_cancel(self, cycle: Cycle) -> R:
        """Calculate the ratio of the cycle

        Args:
            cycle (Cycle): _description_

        Returns:
            R: _description_
        """
        total_cost = sum(self.gra[utx][vtx]["cost"] for (utx, vtx) in cycle)
        total_time = sum(self.gra[utx][vtx]["time"] for (utx, vtx) in cycle)
        return self.T(total_cost) / total_time


class MinCycleRatioSolver(Generic[V, R]):
    """Minimum cost-to-time ratio problem:

    Given: G(V, E)

    Solve:
        max  ratio
        s.t. dist[v] - dist[u] <= cost(u, v) - ratio * time(u, v)
             for all (u, v) in E
    """

    def __init__(self, gra: Mapping[V, Mapping[V, Any]]) -> None:
        """_summary_

        Args:
            gra (Mapping[V, Mapping[V, Any]]): _description_
        """
        self.gra = gra

    def run(self, dist: MutableMapping[V, R], r0: R) -> Tuple[R, Cycle]:
        """_summary_

        Args:
            dist (MutableMapping[V, R]): _description_
            r0 (R): _description_

        Returns:
            Tuple[R, Cycle]: _description_
        """
        # set_default(self.gra, "cost", 1)
        # set_default(self.gra, "time", 1)
        omega = CycleRatioAPI(self.gra, type(r0))
        solver = MaxParametricSolver(self.gra, omega)
        ratio, cycle = solver.run(dist, r0)
        return ratio, cycle
