# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from neg_cycle import *


# def calc_ratio(G, c, ):
#     """Calculate the ratio of the cycle

#     Arguments:
#         G {Networkx Graph} -- [description]
#         handle {Networkx Node} -- [description]
#         pred {dictionary} -- [description]
#         mu {str} -- cost
#         sigma {str} -- time

#     Returns:
#         float -- the ratio
#     """

#     total_cost = sum(G[u][v][mu] for (u, v) in c)
#     total_time = sum(G[u][v][sigma] for (u, v) in c)
#     return total_cost/total_time


# def init_r(G, mu, sigma):
#     max_cost = max(cost for _, _, cost in G.edges.data(mu))
#     min_time = min(time for _, _, time in G.edges.data(sigma))
#     # assume positive time
#     return max_cost * G.number_of_edges() / min_time


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

    # set_default(G, mu, 1)
    # set_default(G, sigma, 1)
    S = negCycleFinder(G)
    # r = init_r(G, mu, sigma)
    C_opt = None
    r_opt = r

    while True:
        for (u, v) in G.edges:
            G[u][v]['weight'] = d(G, r, u, v)

        C = S.neg_cycle_relax()
        if C == None:
            break
        C_opt = C
        r_opt = zero_cancel(G, C)
        if r_opt + 0.0000001 > r:
            break
        r = r_opt
        # update ???
        for (u, v) in C:
            S.dist[u] = S.dist[v] - d(G, r, u, v)

    return r_opt, C_opt, S.dist


# if __name__ == "__main__":
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
