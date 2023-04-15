# -*- coding: utf-8 -*-
from __future__ import print_function

import networkx as nx

from .parametric import max_parametric


def set_default(gra: nx.Graph, weight, value):
    """[summary]

    Arguments:
        gra (nx.Graph): directed graph
        weight ([type]): [description]
        value ([type]): [description]
    """
    for u, v in gra.edges:
        if gra[u][v].get(weight, None) is None:
            gra[u][v][weight] = value


def min_cycle_ratio(gra: nx.Graph, dist):
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
    T = type(dist[next(iter(gra))])

    def calc_weight(r, e):
        """[summary]

        Arguments:
            r ([type]): [description]
            e ([type]): [description]

        Returns:
            [type]: [description]
        """
        u, v = e
        return gra[u][v]["cost"] - r * gra[u][v]["time"]

    def calc_ratio(C):
        """Calculate the ratio of the cycle

        Arguments:
            C {list}: cycle list

        Returns:
            cycle ratio
        """
        total_cost = sum(gra[u][v]["cost"] for (u, v) in C)
        total_time = sum(gra[u][v]["time"] for (u, v) in C)
        return T(total_cost) / total_time

    C0 = nx.find_cycle(gra)
    r0 = calc_ratio(C0)
    r, C = max_parametric(gra, r0, calc_weight, calc_ratio, dist)
    return r, C if C else C0
