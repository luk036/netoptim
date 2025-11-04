from typing import Any, Dict, List, Tuple

import networkx as nx

from netoptim.network_oracle import NetworkOracle


class MockOracle:
    def __init__(self) -> None:
        self.values: Dict[Tuple[Any, Any], float] = {}
        self.grads: Dict[Tuple[Any, Any], float] = {}
        self.t: float = 0.0

    def eval(self, edge: Tuple[Any, Any], x: List[float]) -> float:
        return self.values.get(edge, 0.0)

    def grad(self, edge: Tuple[Any, Any], x: List[float]) -> float:
        return self.grads.get(edge, 0.0)

    def update(self, t: float) -> None:
        self.t = t


def test_network_oracle_update() -> None:
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra: Dict[Any, Dict[Any, Any]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: List[float] = [0.0, 0.0, 0.0]
    oracle = MockOracle()
    net_oracle = NetworkOracle(gra, u, oracle)
    net_oracle.update(1.0)
    assert oracle.t == 1.0


def test_network_oracle_assess_feas_with_negative_cycle() -> None:
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra: Dict[Any, Dict[Any, Any]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: List[float] = [0.0, 0.0, 0.0]
    oracle = MockOracle()
    oracle.values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): -3.0}
    oracle.grads = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): -1.0}
    net_oracle = NetworkOracle(gra, u, oracle)
    x: List[float] = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is not None
    g, f = cut
    assert f == 1.0
    assert g == -1.0


def test_network_oracle_assess_feas_no_negative_cycle() -> None:
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra: Dict[Any, Dict[Any, Any]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: List[float] = [0.0, 0.0, 0.0]
    oracle = MockOracle()
    oracle.values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): 1.0}
    net_oracle = NetworkOracle(gra, u, oracle)
    x: List[float] = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is None
