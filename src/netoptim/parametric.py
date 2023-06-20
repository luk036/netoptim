# -*- coding: utf-8 -*-
from abc import abstractmethod
from .neg_cycle import NegCycleFinder
from typing import Tuple, List, Any
from typing import MutableMapping, Mapping, TypeVar, Generic
from fractions import Fraction


R = TypeVar("R", float, Fraction)  # Comparable field
V = TypeVar("V")
Cycle = List[Tuple[V, V]]


class ParametricAPI(Generic[V, R]):
    @abstractmethod
    def distance(self, ratio: R, edge: Tuple[V, V]) -> R:
        """_summary_

        Args:
            ratio (R): _description_
            edge (Tuple[V, V]): _description_

        Returns:
            R: _description_
        """
        pass

    @abstractmethod
    def zero_cancel(self, cycle: List[Tuple[V, V]]) -> R:
        """_summary_

        Args:
            Cycle (_type_): _description_

        Returns:
            R: _description_
        """
        pass


class MaxParametricSolver(Generic[V, R]):
    """Maximum parametric problem:

    Solve:
        max  ratio
        s.t. dist[v] - dist[u] <= distance(u, v, ratio)
             for all (u, v) in gra
    """

    def __init__(
        self, gra: Mapping[V, Mapping[V, Any]], omega: ParametricAPI[V, R]
    ) -> None:
        """initialize

        Args:
            gra (Mapping[V, Mapping[V, Any]]): _description_
            omega (ParametricAPI): _description_
        """
        self.ncf = NegCycleFinder(gra)
        self.omega = omega

    def run(self, dist: MutableMapping[V, R], ratio: R) -> Tuple[R, Cycle]:
        """run

        Args:
            ratio (R): _description_
            dist (MutableMapping[V, R]): _description_

        Returns:
            Tuple[R, Cycle]: _description_
        """
        r_min = ratio
        c_min = []
        cycle = []

        while True:
            for ci in self.ncf.find_neg_cycle(
                dist, lambda e: self.omega.distance(ratio, e)
            ):
                ri = self.omega.zero_cancel(ci)
                if r_min > ri:
                    r_min = ri
                    c_min = ci
            if r_min >= ratio:
                break

            cycle = c_min
            ratio = r_min
        return ratio, cycle
