# -*- coding: utf-8 -*-
"""
Negative cycle detection for weighed graphs.
1. Based on Howard's policy graph algorithm
2. Looking for more than one negative cycles
"""
from typing import Dict, Callable, Generator, Tuple, List
from typing import MutableMapping, Mapping, TypeVar, Generic, Any
from fractions import Fraction

V = TypeVar("V")  # Hashable
D = TypeVar("D", int, float, Fraction)  # Comparable Ring
Cycle = List[Tuple[V, V]]


class NegCycleFinder(Generic[V]):
    pred: Dict[V, V] = {}

    def __init__(self, gra: Mapping[V, Mapping[V, Any]]) -> None:
        """_summary_

        Args:
            gra (Mapping[V, Mapping[V, Any]]): adjacent list
        """
        self.digraph = gra

    def find_cycle(self) -> Generator[V, None, None]:
        """Find a cycle on the policy graph

        Yields:
            Generator[V, None, None]: node: a start node of the cycle
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

        Args:
            dist (MutableMapping[V, D]): _description_
            get_weight (Callable[[Tuple[V, V]], D]): _description_

        Returns:
            bool: _description_
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
        """_summary_

        Args:
            dist (MutableMapping[V, D]): _description_
            get_weight (Callable[[Tuple[V, V]], D]): _description_

        Yields:
            Generator[Cycle, None, None]: cycle list
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

        Args:
            handle (V): _description_

        Returns:
            Cycle: _description_
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

        Args:
            handle (V): _description_
            dist (MutableMapping[V, Any]): _description_
            get_weight (Callable[[Tuple[V, V]], Any]): _description_

        Returns:
            bool: _description_
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
