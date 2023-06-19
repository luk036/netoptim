# -*- coding: utf-8 -*-
from __future__ import print_function
from .parametric import max_parametric, ParametricAPI, R, V, Cycle
from typing import Tuple, List, Any
from typing import MutableMapping, Mapping, TypeVar
from fractions import Fraction

D = TypeVar("D", int, float, Fraction)  # Comparable Ring


def set_default(gra: Mapping[V, Mapping[V, Any]], weight: D, value: D) -> None:
    """_summary_

    Args:
        gra (Mapping[V, Mapping[V, Any]]): _description_
        weight (D): _description_
        value (D): _description_
    """
    for utx in gra:
        for vtx in gra[utx]:
            if gra[utx][vtx].get(weight, None) is None:
                gra[utx][vtx][weight] = value


class CycleRatioAPI(ParametricAPI):
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


def min_cycle_ratio(gra: Mapping[V, Mapping[V, Any]], dist: MutableMapping[V, R], r0: R) -> Tuple[R, Cycle]:
    """_summary_

    Args:
        gra (Mapping[V, Mapping[V, Any]]): _description_
        dist (MutableMapping[V, R]): _description_
        r0 (R): _description_

    Returns:
        Tuple[R, Cycle]: _description_
    """
    mu = "cost"
    sigma = "time"
    set_default(gra, mu, 1)
    set_default(gra, sigma, 1)
    # T = type(dist[next(iter(gra))])
    omega = CycleRatioAPI(gra, type(r0))
    ratio, cycle = max_parametric(gra, r0, omega, dist)
    return ratio, cycle
