# -*- coding: utf-8 -*-
import networkx as nx
from neg_cycle import negCycleFinder


def max_parametric(G, r, d, zero_cancel):
    """maximum parametric problem:

        max  r
        s.t. dist[v] - dist[v] <= d(u,v,r)
             for all (u, v) in G

    Arguments:
        G {[type]} -- [description]
        r {float} -- parameter to be maximized, initially a large number (infeasible)
        d {[type]} -- monotone decreasing function w.r.t. r
        zero_cancel {[type]} -- [description]

    Returns:
        r_opt -- optimal value
        C_opt -- Most critial cycle
        dist -- optimal sol'n

    """
    def get_weight(G, e):
        return d(G, r, e)

    S = negCycleFinder(G, get_weight)
    C_opt = None
    r_opt = r

    while True:
        # for (u, v) in G.edges:
        #     G[u][v]['weight'] = d(G, r, u, v)

        # r_min = float('Inf')
        # C_min = None
        # for Ci in S.neg_cycle_relax():
        #     ri = zero_cancel(G, Ci)
        #     if r_min > ri:
        #         r_min = ri
        #         C_min = Ci
        C_lst = [C for C in S.neg_cycle_relax()]
        if C_lst is []:
            break
        rlst = [zero_cancel(G, C) for C in C_lst]
        r_min = min(rlst)
        idx = rlst.index(r_min)
        C_min = C_lst[idx]

        if r_min >= r_opt:
            break
        C_opt = C_min
        r_opt = r_min
        # update ???
        for (u, v) in C_opt:
            S.dist[u] = S.dist[v] - get_weight(G, (u, v))

    return r_opt, C_opt, S.dist


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
