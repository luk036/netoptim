# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from neg_cycle import *


def do_case(G):
    #dist = {v: 0 for v in G}
    #pred = {v: None for v in G}

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
    assert c == None