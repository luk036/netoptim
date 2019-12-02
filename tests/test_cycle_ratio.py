# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction

# from networkx.utils import generate_unique_node
from netoptim.min_cycle_ratio import min_cycle_ratio, set_default

from .test_neg_cycle import create_test_case1, create_test_case_timing

# from pprint import pprint


def test_cycle_ratio():
    G = create_test_case1()
    set_default(G, 'time', 1)
    set_default(G, 'cost', 1)
    G[1][2]['cost'] = 5
    dist = list(Fraction(0, 1) for _ in G)
    r, c = min_cycle_ratio(G, dist)
    print(r)
    print(c)
    assert c
    assert r == Fraction(9, 5)


def test_cycle_ratio_timing():
    G = create_test_case_timing()
    set_default(G, 'time',  1)
    G['a1']['a2']['cost'] = 7
    G['a2']['a1']['cost'] = -1
    G['a2']['a3']['cost'] = 3
    G['a3']['a2']['cost'] = 0
    G['a3']['a1']['cost'] = 2
    G['a1']['a3']['cost'] = 4
    # make sure no parallel edges in above!!!
    dist = {v: Fraction(0, 1) for v in G}
    r, c = min_cycle_ratio(G, dist)
    print(r)
    print(c)
    assert c
    assert r == Fraction(1, 1)
