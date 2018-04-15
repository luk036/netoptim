# -*- coding: utf-8 -*-
from __future__ import print_function
from pprint import pprint

from networkx.utils import generate_unique_node
import networkx as nx
from min_cycle_ratio import *


def test_cycle_ratio():
    G = create_test_case1()
    G[1][2]['cost'] = 5
    r, v, pred, dist = min_cycle_ratio(G)
    assert v != None
    print(r)
    print(pred.items())
    print(dist.items())