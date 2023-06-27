from fractions import Fraction
from typing import Generic, List, Mapping, MutableMapping, Tuple, TypeVar

from .parametric import MaxParametricSolver, ParametricAPI

Domain = TypeVar("Domain", int, float, Fraction)  # Comparable Ring
Ratio = TypeVar("Ratio", float, Fraction)  # Comparable field
Node = TypeVar("Node")
Cycle = List[Tuple[Node, Node]]
Graph = Mapping[Node, Mapping[Node, Mapping[str, Domain]]]
GraphMut = MutableMapping[Node, MutableMapping[Node, MutableMapping[str, Domain]]]


def set_default(gra: GraphMut, weight: str, value: Domain) -> None:
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


class CycleRatioAPI(ParametricAPI[Node, Ratio]):
    def __init__(self, gra: GraphMut, K: type) -> None:
        """_summary_

        Args:
            gra (Mapping[Node, Mapping[Node, Any]]): _description_
            T (type): _description_
        """
        self.gra = gra
        self.K = K

    def distance(self, ratio: Ratio, e: Tuple[Node, Node]) -> Ratio:
        """[summary]

        Arguments:
            ratio ([type]): [description]
            e ([type]): [description]

        Returns:
            [type]: [description]
        """
        u, v = e
        return self.gra[u][v]["cost"] - ratio * self.gra[u][v]["time"]

    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """Calculate the ratio of the cycle

        Args:
            cycle (Cycle): _description_

        Returns:
            Ratio: _description_
        """
        total_cost = sum(self.gra[u][v]["cost"] for (u, v) in cycle)
        total_time = sum(self.gra[u][v]["time"] for (u, v) in cycle)
        return self.K(total_cost) / total_time


class MinCycleRatioSolver(Generic[Node, Ratio]):
    """Minimum cost-to-time ratio problem:

    Given: G(Node, E)

    Solve:
        max  ratio
        s.t. dist[v] - dist[u] <= cost(u, v) - ratio * time(u, v)
             for all (u, v) in E
    """

    def __init__(self, gra: Graph) -> None:
        """_summary_

        Args:
            gra (Mapping[Node, Mapping[Node, Any]]): _description_
        """
        self.gra = gra

    def run(self, dist: MutableMapping[Node, Ratio], r0: Ratio) -> Tuple[Ratio, Cycle]:
        """_summary_

        Args:
            dist (MutableMapping[Node, Ratio]): _description_
            r0 (Ratio): _description_

        Returns:
            Tuple[Ratio, Cycle]: _description_
        """
        omega = CycleRatioAPI(self.gra, type(r0))
        solver = MaxParametricSolver(self.gra, omega)
        ratio, cycle = solver.run(dist, r0)
        return ratio, cycle
