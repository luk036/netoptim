# -*- coding: utf-8 -*-
from __future__ import print_function
from .parametric import max_parametric


def set_default(gra, weight, value):
    """[summary]

    Arguments:
        gra (nx.Graph): directed graph
        weight ([type]): [description]
        value ([type]): [description]
    """
    for u in gra:
        for v in gra[u]:
            if gra[u][v].get(weight, None) is None:
                gra[u][v][weight] = value


class CycleRatioAPI:
    def __init__(self, gra, T: type):
        self.gra = gra
        self.T = T

    def distance(self, r, e):
        """[summary]

        Arguments:
            r ([type]): [description]
            e ([type]): [description]

        Returns:
            [type]: [description]
        """
        u, v = e
        return self.gra[u][v]["cost"] - r * self.gra[u][v]["time"]

    def zero_cancel(self, cycle):
        """Calculate the ratio of the cycle

        Arguments:
            cycle {list}: cycle list

        Returns:
            cycle ratio
        """
        total_cost = sum(self.gra[u][v]["cost"] for (u, v) in cycle)
        total_time = sum(self.gra[u][v]["time"] for (u, v) in cycle)
        return self.T(total_cost) / total_time

def min_cycle_ratio(gra, dist, r0):
    """[summary] todo: parameterize cost and time

    Arguments:
        gra ([type]): [description]

    Returns:
        [type]: [description]
    """
    mu = "cost"
    sigma = "time"
    set_default(gra, mu, 1)
    set_default(gra, sigma, 1)
    # T = type(dist[next(iter(gra))])
    omega = CycleRatioAPI(gra, type(r0))
    ratio, cycle = max_parametric(gra, r0, omega, dist)
    return ratio, cycle
