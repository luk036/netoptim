# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from neg_cycle import negCycleFinder


def create_test_case1():
    G = nx.cycle_graph(5, create_using=nx.DiGraph())
    G[1][2]['weight'] = -5
    newnode = generate_unique_node()
    G.add_edges_from([(newnode, n) for n in G])
    return G


def do_case(G):
    N = negCycleFinder(G)
    c = N.find_neg_cycle()
    print(N.pred.items())
    print(N.dist.items())
    return c


def test_cycle():
    G = create_test_case1()
    c = do_case(G)
    assert c != None

    G = nx.path_graph(5, create_using=nx.DiGraph())
    c = do_case(G)
    assert c is None
