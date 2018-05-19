# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from min_cycle_ratio import min_cycle_ratio, set_default
from test_neg_cycle import create_test_case1
from fractions import Fraction
 

def test_cycle_ratio():
    G = create_test_case1()
    set_default(G, 'cost', Fraction(1, 1))
    G[1][2]['cost'] = Fraction(5, 1)
    r, c, dist = min_cycle_ratio(G)
    assert c != None
    assert r == Fraction(9, 5)
    print(r)
    print(c)
    print(dist.items())
