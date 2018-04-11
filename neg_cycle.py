# -*- coding: utf-8 -*-
"""
Negative cycle detection for weighed graphs.
(based on Bellman-Ford algorithm)
"""

from collections import deque
import networkx as nx


class negCycleFinder:

    def __init__(self, G, source):
        """Relaxation loop for Bellman–Ford algorithm

        Parameters
        ----------
        G : NetworkX graph

        source: list
            List of source nodes

        Raises
        ------
        NetworkXUnbounded
           If the (di)graph contains a negative cost (di)cycle, the
           algorithm raises an exception to indicate the presence of the
           negative cost (di)cycle.  Note: any negative weight edge in an
           undirected graph is a negative cost cycle
        """
        self.G = G
        self.source = source

        if source not in G:
            raise KeyError("Node %s is not found in the graph" % source)

        self.q = deque([source])
        self.in_q = set([source])
        self.dist = {source: 0}
        self.pred = {source: None}

    def find_neg_cycle(self, weight='weight'):
        """Compute negative cycle in weighted graphs.

        The algorithm has a running time of O(mn) where n is the number of
        nodes and m is the number of edges.

        Parameters
        ----------
        weight: string, optional (default='weight')
           Edge data key corresponding to the edge weight

        Returns
        -------
        pred, dist : dictionaries
           Returns two dictionaries keyed by node to predecessor in the
           negative cycle and to the distance from the source respectively.

        Notes
        -----
        Edge weight attributes must be numerical.
        Distances are calculated as sums of weighted edges traversed.

        The dictionaries returned only have keys for nodes reachable from
        the source.

        In the case where the (di)graph is not connected, if a component
        not containing the source contains a negative cost (di)cycle, it
        will not be detected.

        """
        for u, v, attr in self.G.selfloop_edges(data=True):
            if attr.get(weight, 1) < 0:
                raise nx.NetworkXUnbounded(
                    "Self loop negative cost cycle detected.")

        if len(self.G) == 1:
            return None

        if self.q:
            source = self.q.popleft()
            self.q.append(source)
        else:
            source = self.source
            self.q.append(source)
            self.in_q = set([source])

        self.dist = {source: 0}
        self.pred = {source: None}

        v = self.neg_cycle_relaxation(self.pred, self.dist, [source], weight)
        return v


    def neg_cycle_relaxation(self, pred, dist, source, weight):
        """Relaxation loop for Bellman–Ford algorithm

        Parameters
        ----------
        G : NetworkX graph

        pred: dict
            Keyed by node to predecessor in the path

        dist: dict
            Keyed by node to the distance from the source

        source: list
            List of source nodes

        weight: string
           Edge data key corresponding to the edge weight

        Returns
        -------
        Returns two dictionaries keyed by node to predecessor in the
           path and to the distance from the source respectively.

        Raises
        ------
        NetworkXUnbounded
           If the (di)graph contains a negative cost (di)cycle, the
           algorithm raises an exception to indicate the presence of the
           negative cost (di)cycle.  Note: any negative weight edge in an
           undirected graph is a negative cost cycle
        """
        G = self.G
        if G.is_multigraph():
            def get_weight(edge_dict):
                return min(eattr.get(weight, 1) for eattr in edge_dict.values())
        else:
            def get_weight(edge_dict):
                return edge_dict.get(weight, 1)

        G_succ = G.succ if G.is_directed() else G.adj
        inf = float('inf')
        n = len(G)

        count = {}
        # q = deque(source)
        # in_q = set(source)
        q = self.q
        in_q = self.in_q
        while q:
            u = q.popleft()
            in_q.remove(u)
            # Skip relaxations if the predecessor of u is in the queue.
            if pred[u] not in in_q:
                dist_u = dist[u]
                for v, e in G_succ[u].items():
                    dist_v = dist_u + get_weight(e)
                    if dist_v < dist.get(v, inf):
                        if v not in in_q:
                            count_v = count.get(v, 0) + 1
                            if count_v == n:
                                return v
                            q.append(v)
                            in_q.add(v)
                            count[v] = count_v
                        dist[v] = dist_v
                        pred[v] = u

        return None

