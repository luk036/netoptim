# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from neg_cycle import *


def calc_ratio(G, c, mu, sigma):
    """Calculate the ratio of the cycle

    Arguments:
        G {Networkx Graph} -- [description]
        handle {Networkx Node} -- [description]
        pred {dictionary} -- [description]
        mu {str} -- cost
        sigma {str} -- time

    Returns:
        float -- the ratio
    """

    total_cost = sum(G[u][v][mu] for (u, v) in c)
    total_time = sum(G[u][v][sigma] for (u, v) in c)
    return total_cost/total_time


def init_r(G, mu, sigma):
    max_cost = max(cost for _, _, cost in G.edges.data(mu))
    min_time = min(time for _, _, time in G.edges.data(sigma))
    # assume positive time
    return max_cost * G.number_of_edges() / min_time


def update_cycle(G, c, r, dist, mu, sigma):
    """Calculate the ratio of the cycle

    Arguments:
        G {Networkx Graph} -- [description]
        handle {Networkx Node} -- [description]
        pred {dictionary} -- [description]
        mu {str} -- cost
        sigma {str} -- time
    """

    for (u, v) in c:
        wt = G[u][v][mu] - r * G[u][v][sigma]
        dist[u] = dist[v] - wt


def min_cycle_ratio(G, mu='cost', sigma='time'):
    set_default(G, mu, 1)
    set_default(G, sigma, 1)
    detector = negCycleFinder(G)
    r = init_r(G, mu, sigma)
    c_keep = None

    while True:
        for (u, v) in G.edges:
            wt = G[u][v][mu] - r * G[u][v][sigma]
            G[u][v]['weight'] = wt

        c = detector.neg_cycle_relax()
        if c == None:
            break
        c_keep = c
        r_new = calc_ratio(G, c, mu, sigma)
        if r_new + 0.0000001 > r:
            break
        r = r_new
        update_cycle(G, c, r, detector.dist, mu, sigma)
    return r, c_keep, detector.dist


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
