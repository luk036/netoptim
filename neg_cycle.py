# -*- coding: utf-8 -*-
"""
Negative cycle detection for weighed graphs.
(based on Bellman-Ford algorithm)
"""
from __future__ import print_function
from pprint import pprint

from collections import deque
import networkx as nx


class negCycleFinder:

    def __init__(self, G):
        """Relaxation loop for Bellman–Ford algorithm

        Parameters
        ----------
        G : NetworkX graph
        """

        self.G = G
        self.dist = {v: 0 for v in self.G.nodes}
        self.pred = {v: None for v in self.G.nodes}

    def find_cycle(self, G, pred):
        """Find a cycle on policy graph

        Arguments:
            G {NetworkX graph} 
            pred {dictionary} -- policy graph

        Returns:
            handle -- a start node of the cycle
        """

        visited = {v: None for v in G.nodes}
        for v in G.nodes:
            if visited[v] != None:
                continue
            u = v
            while True:
                visited[u] = v
                u = pred[u]
                if u == None:
                    break
                if visited[u] != None:
                    break
            if u == None:
                continue
            if visited[u] == v:
                return v
        return None

    def relax(self, G, dist, pred, weight='weight'):
        """Perform a updating of dist and pred

        Arguments:
            G {NetworkX graph} -- [description]
            dist {dictionary} -- [description]
            pred {dictionary} -- [description]

        Keyword Arguments:
            weight {str} -- [description] (default: {'weight'})

        Returns:
            [type] -- [description]
        """

        changed = False
        for (u, v, wt) in G.edges.data(weight):
            dist_new = dist[u] + wt
            if dist[v] > dist_new:
                dist[v] = dist_new
                pred[v] = u
                changed = True
        return changed

    def find_neg_cycle(self, weight='weight'):
        """Perform a updating of dist and pred

        Arguments:
            G {[type]} -- [description]
            dist {dictionary} -- [description]
            pred {dictionary} -- [description]

        Keyword Arguments:
            weight {str} -- [description] (default: {'weight'})

        Returns:
            [type] -- [description]
        """
        self.dist = {v: 0. for v in self.G.nodes}
        self.pred = {v: None for v in self.G.nodes}
        G = self.G
        for (u, v) in G.edges:
            if not G[u][v].get(weight, None):
                G[u][v][weight] = 1

        v = self.neg_cycle_relax(weight)
        return v

    def neg_cycle_relax(self, weight):
        dist = self.dist
        pred = self.pred
        G = self.G
        while True:
            changed = self.relax(G, dist, pred, weight)
            if changed:
                v = self.find_cycle(G, pred)
                if v != None:
                    return v
            else:
                break
        return None



if __name__ == "__main__":
    from networkx.utils import generate_unique_node
    import networkx as nx

    G = nx.cycle_graph(5, create_using=nx.DiGraph())
    G[1][2]['weight'] = -5
    newnode = generate_unique_node()
    G.add_edges_from([(newnode, n) for n in G])

    N = negCycleFinder(G)
    v = N.find_neg_cycle()
    # assert v == 0
    print(v)
    print(N.pred.items())
    print(N.dist.items())

    #dist = {newnode: 0}
    #pred = {newnode: None}
    v = N.find_neg_cycle()
    # assert v == 0
    print(v)
    print(N.pred.items())
    print(N.dist.items())

    source = 0
    #dist = {source: 0}
    #pred = {source: None}
    G = nx.path_graph(5, create_using=nx.DiGraph())
    M = negCycleFinder(G)
    v = M.find_neg_cycle()
    assert v == None
    print(M.pred.items())
    print(M.dist.items())

    v = M.find_neg_cycle()
    assert v == None
    print(M.pred.items())
    print(M.dist.items())
