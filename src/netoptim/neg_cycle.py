# -*- coding: utf-8 -*-
"""
Negative cycle detection for weighed graphs.
1. Support Lazy evalution
"""
from typing import Dict


class NegCycleFinder:
    pred: Dict = {}

    def __init__(self, gra):
        """[summary]

        Arguments:
            gra: Graph
        """
        self.gra = gra

    def find_cycle(self):
        """Find a cycle on the policy graph

        Yields:
            node: a start node of the cycle
        """
        visited = {}
        for v in filter(lambda v: v not in visited, self.gra):
            u = v
            while True:
                visited[u] = v
                if u not in self.pred:
                    break
                u = self.pred[u]
                if u in visited:
                    if visited[u] == v:
                        yield u
                    break

    def relax(self, dist, get_weight):
        """Perform a updating of dist and pred

        Arguments:
            dist (Union[List, Dict]): [description]
            get_weight (Callable): [description]

        Returns:
            [type]: [description]
        """
        changed = False
        for u in self.gra:
            for v in self.gra.neighbors(u):
                wt = get_weight((u, v))
                d = dist[u] + wt
                if dist[v] > d:
                    dist[v] = d
                    self.pred[v] = u
                    changed = True
        return changed

    def find_neg_cycle(self, dist, get_weight):
        """Perform a updating of dist and pred

        Arguments:
            dist (Union[List, Dict]): [description]
            get_weight (Callable): [description]

        Yields:
            list of edges: cycle list
        """
        # self.dist = list(0 for _ in self.gra)
        self.pred = {}
        found = False
        while not found and self.relax(dist, get_weight):
            # v = self.find_cycle()
            for v in self.find_cycle():
                # Will zero cycle be found???
                assert self.is_negative(v, dist, get_weight)
                found = True
                yield self.cycle_list(v)

    def cycle_list(self, handle):
        """Cycle list started from handle

        Arguments:
            handle: graph node

        Returns:
            list of edges: cycle list
        """
        v = handle
        cycle = list()
        while True:
            u = self.pred[v]
            cycle += [(u, v)]
            v = u
            if v == handle:
                break
        return cycle

    def is_negative(self, handle, dist, get_weight):
        """Check if the cycle list is negative

        Arguments:
            handle: graph node
            get_weight (Callable): [description]

        Returns:
            bool: [description]
        """
        v = handle
        # do while loop in C++
        while True:
            u = self.pred[v]
            wt = get_weight((u, v))
            if dist[v] > dist[u] + wt:
                return True
            v = u
            if v == handle:
                break
        return False
