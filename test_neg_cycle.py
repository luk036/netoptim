# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from neg_cycle import *

def test_cycle():
    G = nx.cycle_graph(5, create_using=nx.DiGraph())
    G[1][2]['weight'] = -5
    newnode = generate_unique_node()
    G.add_edges_from([(newnode, n) for n in G])

    N = negCycleFinder(G, newnode)
    v = N.find_neg_cycle()
    assert v == 0
    print (sorted(N.pred.items()))
    print (sorted(N.dist.items()))

    #dist = {newnode: 0}
    #pred = {newnode: None}
    v = N.find_neg_cycle()
    assert v == 0
    print (sorted(N.pred.items()))
    print (sorted(N.dist.items()))

    source = 0
    #dist = {source: 0}
    #pred = {source: None}
    G = nx.path_graph(5, create_using=nx.DiGraph())
    M = negCycleFinder(G, source)
    v = M.find_neg_cycle()
    assert v == None
    print (sorted(M.pred.items()))
    print (sorted(M.dist.items()))

    v = M.find_neg_cycle()
    assert v == None
    print (sorted(M.pred.items()))
    print (sorted(M.dist.items()))
