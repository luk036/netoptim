# -*- coding: utf-8 -*-
from __future__ import print_function

# from networkx.utils import generate_unique_node
import networkx as nx

from netoptim.lict import Lict, TinyDiGraph
from netoptim.neg_cycle import NegCycleFinder


def create_test_case1():
    """[summary]

    Returns:
        [type]: [description]
    """
    gra = nx.cycle_graph(5, create_using=nx.DiGraph())
    gra[1][2]['weight'] = -5
    gra.add_edges_from([(5, n) for n in gra])
    return gra


def create_test_case_timing():
    """[summary]

    Returns:
        [type]: [description]
    """
    gra = nx.DiGraph()
    nodelist = ['a1', 'a2', 'a3']
    gra.add_nodes_from(nodelist)
    gra.add_edges_from([
        ('a1', 'a2', {'weight': 7}),
        ('a2', 'a1', {'weight': 0}),
        ('a2', 'a3', {'weight': 3}),
        ('a3', 'a2', {'weight': 1}),
        ('a3', 'a1', {'weight': 2}),
        ('a1', 'a3', {'weight': 5})
    ])
    return gra


def create_tiny_graph():
    """[summary]

    Returns:
        [type]: [description]
    """
    gra = TinyDiGraph()
    gra.init_nodes(3)
    gra.add_edges_from([
        (0, 1, {'weight': 7}),
        (1, 0, {'weight': 0}),
        (1, 2, {'weight': 3}),
        (2, 1, {'weight': 1}),
        (2, 0, {'weight': 2}),
        (0, 2, {'weight': 5})
    ])
    return gra


def do_case(gra, dist):
    """[summary]

    Arguments:
        gra ([type]): [description]

    Returns:
        [type]: [description]
    """
    def get_weight(e):
        u, v = e
        return gra[u][v].get('weight', 1)

    N = NegCycleFinder(gra)
    hasNeg = False
    for _ in N.find_neg_cycle(dist, get_weight):
        hasNeg = True
        break
    return hasNeg


def test_neg_cycle():
    gra = create_test_case1()
    dist = list(0 for _ in gra)
    hasNeg = do_case(gra, dist)
    assert hasNeg


def test_no_neg_cycle():
    gra = nx.path_graph(5, create_using=nx.DiGraph())
    dist = list(0 for _ in gra)
    hasNeg = do_case(gra, dist)
    assert not hasNeg


def test_timing_graph():
    gra = create_test_case_timing()
    dist = {v: 0 for v in gra}
    hasNeg = do_case(gra, dist)
    assert not hasNeg


def test_tiny_graph():
    gra = create_tiny_graph()
    dist = Lict([0, 0, 0])
    hasNeg = do_case(gra, dist)
    assert not hasNeg
