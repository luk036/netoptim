# -*- coding: utf-8 -*-
from .neg_cycle import negCycleFinder


def max_parametric(G, r_opt, C_opt, d, zero_cancel, dist):
    """maximum parametric problem:

        max  r
        s.t. dist[v] - dist[v] <= d(u, v, r)
             for all (u, v) in G

    Arguments:
        G {[type]} -- directed graph
        r {float} -- parameter to be maximized, initially a large number (infeasible)
        d {[type]} -- monotone decreasing function w.r.t. r
        zero_cancel {[type]} -- [description]

    Returns:
        r_opt -- optimal value
        C_opt -- Most critial cycle
        dist -- optimal sol'n
    """
    def get_weight(G, e):
        return d(G, r_opt, e)

    S = negCycleFinder(G)
    # C_opt = None
    r_min = r_opt

    while True:
        C_min = None
        for C in S.find_neg_cycle(dist, get_weight):
            r_min = zero_cancel(G, C)
            C_min = C
            break  # get only first one

        if C_min is None:
            break

        if r_min >= r_opt:
            break

        C_opt = C_min
        r_opt = r_min
        # update ???
        for e in C_opt:
            u, v = e
            # i_v = G.nodemap[v]
            # i_u = G.nodemap[u]
            dist[u] = dist[v] - get_weight(G, e)

    return r_opt, C_opt


# if __name__ == "__main__":
#     from __future__ import print_function
#     from pprint import pprint
#     import networkx as nx
#     from neg_cycle import *
#     from networkx.utils import generate_unique_node

#     G = create_test_case1()
#     G[1][2]['cost'] = 5
#     r, c, dist = min_cycle_ratio(G)
#     assert c != None
#     print(r)
#     print(c)
#     print(dist.items())

#     G = nx.cycle_graph(5, create_using=nx.DiGraph())
#     G[1][2]['cost'] = -6.
#     newnode = generate_unique_node()
#     G.add_edges_from([(newnode, n) for n in G])
#     r, c, dist = min_cycle_ratio(G)
#     assert c != None
#     print(r)
#     print(c)
#     print(dist.items())
