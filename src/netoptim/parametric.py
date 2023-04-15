# -*- coding: utf-8 -*-
from .neg_cycle import NegCycleFinder


def max_parametric(gra, r, d, zero_cancel, dist, pick_one_only=False):
    """maximum parametric problem:

        max  r
        s.t. dist[v] - dist[v] <= d(u, v, r)
             for all (u, v) in gra

    Arguments:
        gra ([type]): directed graph
        r {float}: parameter to be maximized, initially a big number!!!
        d ([type]): monotone decreasing function w.r.t. r
        zero_cancel ([type]): [description]
        pick_one_only {bool}: [description]

    Returns:
        r: optimal value
        C: Most critial cycle
        dist: optimal sol'n
    """

    def get_weight(e):
        return d(r, e)

    S = NegCycleFinder(gra)
    r_min = r
    C = []

    while True:
        for Ci in S.find_neg_cycle(dist, get_weight):
            ri = zero_cancel(Ci)
            if r_min > ri:
                r_min = ri
                C_min = Ci
                if pick_one_only:
                    break
        if r_min >= r:
            break

        C = C_min
        r = r_min
    return r, C


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
