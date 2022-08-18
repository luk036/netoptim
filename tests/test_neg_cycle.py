# -*- coding: utf-8 -*-
from __future__ import print_function

# from networkx.utils import generate_unique_node
import networkx as nx

from netoptim.neg_cycle import NegCycleFinder
from netoptim.lict import Lict, TinyDiGraph


def create_test_case1():
    """[summary]

    Returns:
        [type]: [description]
    """
    G = nx.cycle_graph(5, create_using=nx.DiGraph())
    G[1][2]['weight'] = -5
    G.add_edges_from([(5, n) for n in G])
    return G


def create_test_case_timing():
    """[summary]

    Returns:
        [type]: [description]
    """
    G = nx.DiGraph()
    nodelist = ['a1', 'a2', 'a3']
    G.add_nodes_from(nodelist)
    G.add_edges_from([
        ('a1', 'a2', {'weight': 7}),
        ('a2', 'a1', {'weight': 0}),
        ('a2', 'a3', {'weight': 3}),
        ('a3', 'a2', {'weight': 1}),
        ('a3', 'a1', {'weight': 2}),
        ('a1', 'a3', {'weight': 5})
    ])
    return G


def create_tiny_graph():
    """[summary]

    Returns:
        [type]: [description]
    """
    G = TinyDiGraph()
    G.init_nodes(3)
    G.add_edges_from([
        (0, 1, {'weight': 7}),
        (1, 0, {'weight': 0}),
        (1, 2, {'weight': 3}),
        (2, 1, {'weight': 1}),
        (2, 0, {'weight': 2}),
        (0, 2, {'weight': 5})
    ])
    return G


def do_case(G, dist):
    """[summary]

    Arguments:
        G ([type]): [description]

    Returns:
        [type]: [description]
    """
    def get_weight(e):
        u, v = e
        return G[u][v].get('weight', 1)

    N = NegCycleFinder(G)
    hasNeg = False
    for _ in N.find_neg_cycle(dist, get_weight):
        hasNeg = True
        break
    return hasNeg


def test_neg_cycle():
    G = create_test_case1()
    dist = list(0 for _ in G)
    hasNeg = do_case(G, dist)
    assert hasNeg


def test_no_neg_cycle():
    G = nx.path_graph(5, create_using=nx.DiGraph())
    dist = list(0 for _ in G)
    hasNeg = do_case(G, dist)
    assert not hasNeg


def test_timing_graph():
    G = create_test_case_timing()
    dist = {v: 0 for v in G}
    hasNeg = do_case(G, dist)
    assert not hasNeg


def test_tiny_graph():
    G = create_tiny_graph()
    dist = Lict([0, 0, 0])
    hasNeg = do_case(G, dist)
    assert not hasNeg
