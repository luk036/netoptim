# -*- coding: utf-8 -*-
"""
Negative cycle detection for weighed graphs.
1. Based on Howard's policy graph algorithm
2. Looking for more than one negative cycles
"""
from typing import Dict, Callable, Generator, Sequence, Tuple, List
from typing import MutableMapping, Mapping, TypeVar, Generic, Any
from fractions import Fraction

V = TypeVar("V")  # Hashable
D = TypeVar("D", int, float, Fraction)  # Comparable Ring
Digraph = Mapping[V, Sequence[V]]
Cycle = List[Tuple[V, V]]


class NegCycleFinder(Generic[V]):
    pred: Dict[V, V] = {}

    def __init__(self, gra: Mapping[V, Sequence[V]]) -> None:
        """[summary]

        Arguments:
            gra: directed graph
        """
        self.digraph = gra

    def find_cycle(self) -> Generator[V, None, None]:
        """Find a cycle on the policy graph

        Yields:
            node: a start node of the cycle
        """
        visited: Dict[V, V] = {}
        for vtx in filter(lambda vtx: vtx not in visited, self.digraph):
            utx = vtx
            while True:
                visited[utx] = vtx
                if utx not in self.pred:
                    break
                utx = self.pred[utx]
                if utx in visited:
                    if visited[utx] == vtx:
                        yield utx
                    break

    def relax(
        self, dist: MutableMapping[V, D], get_weight: Callable[[Tuple[V, V]], D]
    ) -> bool:
        """Perform a updating of dist and pred

        Arguments:
            dist (Union[List, Dict]): [description]
            get_weight (Callable): [description]

        Returns:
            [type]: [description]
        """
        changed = False
        for utx in self.digraph:
            for vtx in self.digraph[utx]:
                weight = get_weight((utx, vtx))
                distance = dist[utx] + weight
                if dist[vtx] > distance:
                    dist[vtx] = distance
                    self.pred[vtx] = utx
                    changed = True
        return changed

    def find_neg_cycle(
        self, dist: MutableMapping[V, D], get_weight: Callable[[Tuple[V, V]], D]
    ) -> Generator[Cycle, None, None]:
        """Perform a updating of dist and pred

        Arguments:
            dist (Union[List, Dict]): [description]
            get_weight (Callable): [description]

        Yields:
            list of edges: cycle list
        """
        self.pred = {}
        found = False
        while not found and self.relax(dist, get_weight):
            for vtx in self.find_cycle():
                # Will zero cycle be found???
                assert self.is_negative(vtx, dist, get_weight)
                found = True
                yield self.cycle_list(vtx)

    def cycle_list(self, handle: V) -> Cycle:
        """Cycle list started from handle

        Arguments:
            handle: graph node

        Returns:
            list of edges: cycle list
        """
        vtx = handle
        cycle = list()
        while True:
            utx = self.pred[vtx]
            cycle += [(utx, vtx)]
            vtx = utx
            if vtx == handle:
                break
        return cycle

    def is_negative(
        self,
        handle: V,
        dist: MutableMapping[V, Any],
        get_weight: Callable[[Tuple[V, V]], Any],
    ) -> bool:
        """Check if the cycle list is negative

        Arguments:
            handle: graph node
            get_weight (Callable): [description]

        Returns:
            bool: [description]
        """
        vtx = handle
        # do while loop in C++
        while True:
            utx = self.pred[vtx]
            weight = get_weight((utx, vtx))
            if dist[vtx] > dist[utx] + weight:
                return True
            vtx = utx
            if vtx == handle:
                break
        return False
