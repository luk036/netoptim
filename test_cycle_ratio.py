# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from min_cycle_ratio import *

def test_cycle_ratio():
    G = nx.cycle_graph(5, create_using=nx.DiGraph())
    G[1][2]['cost'] = 5
    newnode = generate_unique_node()
    G.add_edges_from([(newnode, n) for n in G])
    r, v, pred, dist = min_cycle_ratio(G)
    assert v != None
    print(r)
    print(pred.items())
    print(dist.items())
