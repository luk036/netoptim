# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from .neg_cycle import NegCycleFinder
from typing import Tuple, List, Any
from typing import MutableMapping, Mapping, TypeVar
from fractions import Fraction


R = TypeVar("R", float, Fraction)  # Comparable field
V = TypeVar("V")
Cycle = List[Tuple[V, V]]


class ParametricAPI(ABC):
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
    def zero_cancel(self, Cycle) -> R:
        """_summary_

        Args:
            Cycle (_type_): _description_

        Returns:
            R: _description_
        """
        pass


def max_parametric(
    gra: Mapping[V, Mapping[V, Any]],
    ratio: R,
    omega: ParametricAPI,
    dist: MutableMapping[V, R],
) -> Tuple[R, Cycle]:
    """Maximum parametric problem:

        max  ratio
        s.t. dist[vtx] - dist[vtx] <= distance(utx, vtx, ratio)
             for all (utx, vtx) in gra

    Args:
        gra (Mapping[V, Mapping[V, Any]]): _description_
        ratio (R): _description_
        omega (ParametricAPI): _description_
        dist (MutableMapping[V, R]): _description_

    Returns:
        Tuple[R, Cycle]: _description_
    """

    def get_weight(edge: Tuple[V, V]) -> R:
        """_summary_

        Args:
            edge (Tuple[V, V]): _description_

        Returns:
            R: _description_
        """
        return omega.distance(ratio, edge)

    ncf = NegCycleFinder(gra)
    r_min = ratio
    c_min = []
    cycle = []

    while True:
        for ci in ncf.find_neg_cycle(dist, get_weight):
            ri = omega.zero_cancel(ci)
            if r_min > ri:
                r_min = ri
                c_min = ci
        if r_min >= ratio:
            break

        cycle = c_min
        ratio = r_min
    return ratio, cycle
