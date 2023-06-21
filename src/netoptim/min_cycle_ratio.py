from fractions import Fraction
from typing import Generic, List, Mapping, MutableMapping, Tuple, TypeVar

from .parametric import MaxParametricSolver, ParametricAPI

D = TypeVar("D", int, float, Fraction)  # Comparable Ring
R = TypeVar("R", float, Fraction)  # Comparable field
V = TypeVar("V")
Cycle = List[Tuple[V, V]]
Graph = Mapping[V, Mapping[V, Mapping[str, D]]]
GraphMut = MutableMapping[V, MutableMapping[V, MutableMapping[str, D]]]


def set_default(gra: GraphMut, weight: str, value: D) -> None:
    """_summary_

    Args:
        gra (Graph): _description_
        weight (str): _description_
        value (Any): _description_
    """
    for u in gra:
        for v in gra[u]:
            if gra[u][v].get(weight, None) is None:
                gra[u][v][weight] = value


class CycleRatioAPI(ParametricAPI[V, R]):
    def __init__(self, gra: GraphMut, K: type) -> None:
        """_summary_

        Args:
            gra (Mapping[V, Mapping[V, Any]]): _description_
            T (type): _description_
        """
        self.gra = gra
        self.K = K

    def distance(self, ratio: R, e: Tuple[V, V]) -> R:
        """[summary]

        Arguments:
            ratio ([type]): [description]
            e ([type]): [description]

        Returns:
            [type]: [description]
        """
        u, v = e
        return self.gra[u][v]["cost"] - ratio * self.gra[u][v]["time"]

    def zero_cancel(self, cycle: Cycle) -> R:
        """Calculate the ratio of the cycle

        Args:
            cycle (Cycle): _description_

        Returns:
            R: _description_
        """
        total_cost = sum(self.gra[u][v]["cost"] for (u, v) in cycle)
        total_time = sum(self.gra[u][v]["time"] for (u, v) in cycle)
        return self.K(total_cost) / total_time


class MinCycleRatioSolver(Generic[V, R]):
    """Minimum cost-to-time ratio problem:

    Given: G(V, E)

    Solve:
        max  ratio
        s.t. dist[v] - dist[u] <= cost(u, v) - ratio * time(u, v)
             for all (u, v) in E
    """

    def __init__(self, gra: Graph) -> None:
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
        omega = CycleRatioAPI(self.gra, type(r0))
        solver = MaxParametricSolver(self.gra, omega)
        ratio, cycle = solver.run(dist, r0)
        return ratio, cycle
