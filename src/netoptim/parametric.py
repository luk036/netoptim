# -*- coding: utf-8 -*-
from .neg_cycle import NegCycleFinder
from typing import Sequence, Tuple, List
from typing import MutableMapping, Mapping, TypeVar
from fractions import Fraction

R = TypeVar("R", float, Fraction)  # Comparable field
V = TypeVar("V")
Cycle = List[Tuple[V, V]]


def max_parametric(
    gra: Mapping[V, Sequence[V]],
    ratio: R,
    omega,
    # distance: Callable[[R, Tuple[V, V]], R],
    # zero_cancel: Callable[[Cycle], R],
    dist: MutableMapping[V, R],
):
    """maximum parametric problem:

        max  ratio
        s.t. dist[v] - dist[v] <= distance(u, v, ratio)
             for all (u, v) in gra

    Arguments:
        gra ([type]): directed graph
        ratio {float}: parameter to be maximized, initially a big number!!!
        d ([type]): monotone decreasing function w.r.t. r
        zero_cancel ([type]): [description]
        pick_one_only {bool}: [description]

    Returns:
        ratio: optimal value
        C: Most critial cycle
        dist: optimal sol'n
    """

    def get_weight(edge: Tuple[V, V]) -> R:
        return omega.distance(ratio, edge)

    ncf = NegCycleFinder(gra)
    r_min = ratio
    c_min = []
    cycle = []
    K = type(ratio)

    while True:
        for ci in ncf.find_neg_cycle(dist, get_weight):
            cost, time = omega.zero_cancel(ci)
            ri = K(cost) / time
            if r_min > ri:
                r_min = ri
                c_min = ci
        if r_min >= ratio:
            break

        cycle = c_min
        ratio = r_min
    return ratio, cycle


# if __name__ == "__main__":
#     from __future__ import print_function
#     from pprint import pprint
#     import networkx as nx
#     from neg_cycle import *
#     from networkx.utils import generate_unique_node

#     gra = create_test_case1()
#     gra[1][2]['cost'] = 5
#     r, c, dist = min_cycle_ratio(gra)
#     assert c != None
#     print(r)
#     print(c)
#     print(dist.items())

#     gra = nx.cycle_graph(5, create_using=nx.DiGraph())
#     gra[1][2]['cost'] = -6.
#     newnode = generate_unique_node()
#     gra.add_edges_from([(newnode, n) for n in gra])
#     r, c, dist = min_cycle_ratio(gra)
#     assert c != None
#     print(r)
#     print(c)
#     print(dist.items())
