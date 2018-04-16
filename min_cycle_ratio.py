# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from neg_cycle import *


def calc_ratio(G, handle, pred, mu, sigma):
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

    v = handle
    total_cost = 0.
    total_time = 0.
    while True:
        u = pred[v]
        total_cost += G[u][v][mu]
        total_time += G[u][v][sigma]
        v = u
        if v == handle:
            break
    return total_cost/total_time


def update_cycle(G, handle, r, dist, pred, mu, sigma):
    """Calculate the ratio of the cycle
    
    Arguments:
        G {Networkx Graph} -- [description]
        handle {Networkx Node} -- [description]
        pred {dictionary} -- [description]
        mu {str} -- cost
        sigma {str} -- time
    """

    v = handle
    dist[v] = 0.
    while True:
        u = pred[v]
        wt = G[u][v][mu] - r * G[u][v][sigma]
        dist[u] = dist[v] - wt 
        v = u
        if v == handle:
            break

def min_cycle_ratio(G, mu='cost', sigma='time'):
    set_default(G, mu, 1)
    set_default(G, sigma, 1)
    # dist = {v: 0. for v in G}
    pred = {v: None for v in G}
    handle = None
    detector = negCycleFinder(G)
    max_cost = float('-inf')
    min_time = float('inf')
    for (u, v) in G.edges:
        if max_cost < G[u][v][mu]:
            max_cost = G[u][v][mu]
        if min_time > G[u][v][sigma]:
            min_time = G[u][v][sigma]
    r = max_cost * G.number_of_edges() / min_time # assume non-negative cost and time

    while True:
        for (u, v) in G.edges:
            G[u][v]['weight'] = G[u][v][mu] - r * G[u][v][sigma]
        v = detector.neg_cycle_relax()
        if v == None:
            break
        pred = detector.pred.copy()
        handle = v
        r = calc_ratio(G, handle, pred, mu, sigma)
        update_cycle(G, handle, r, detector.dist, pred, mu, sigma)
    return r, handle, pred, detector.dist


if __name__ == "__main__":
    import networkx as nx

    G = nx.cycle_graph(5, create_using=nx.DiGraph())
    G[1][2]['cost'] = 6.
    newnode = generate_unique_node()
    G.add_edges_from([(newnode, n) for n in G])
    r, v, pred, dist = min_cycle_ratio(G)
    assert v != None
    print(r)
    print(pred.items())
    print(dist.items())
