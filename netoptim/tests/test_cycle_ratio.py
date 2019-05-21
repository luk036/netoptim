# -*- coding: utf-8 -*-
from __future__ import print_function
# from pprint import pprint

# from networkx.utils import generate_unique_node
# import networkx as nx
from ..min_cycle_ratio import min_cycle_ratio, set_default
from .test_neg_cycle import create_test_case1, create_test_case_timing
from fractions import Fraction


def test_cycle_ratio():
    G = create_test_case1()
    set_default(G, 'cost', Fraction(1, 1))
    G[1][2]['cost'] = Fraction(5, 1)
    r, c, _ = min_cycle_ratio(G)
    assert c != None
    assert r == Fraction(9, 5)
    print(r)
    print(c)


def test_cycle_ratio_timing():
    G = create_test_case_timing()
    set_default(G, 'time', Fraction(1, 1))
    G['a1']['a2']['cost'] = Fraction(7, 1)
    G['a2']['a1']['cost'] = Fraction(-1, 1)
    G['a2']['a3']['cost'] = Fraction(3, 1)
    G['a3']['a2']['cost'] = Fraction(0, 1)
    G['a3']['a1']['cost'] = Fraction(2, 1)
    G['a1']['a3']['cost'] = Fraction(4, 1)
    # make sure no parallel edges in above!!!

    r, c, _ = min_cycle_ratio(G)
    assert c != None
    assert r == Fraction(3, 2)
