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


def create_large_graph(num_nodes: int) -> nx.DiGraph:
    """Create a large graph."""
    G = nx.DiGraph()
    for i in range(num_nodes):
        G.add_edge(i, (i + 1) % num_nodes)
    return G


def test_network_oracle_stress_no_negative_cycle() -> None:
    """Test with a large graph and no negative cycles."""
    num_nodes = 1000
    G = create_large_graph(num_nodes)
    gra: Dict[Any, Dict[Any, Any]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: List[float] = [0.0] * num_nodes
    oracle = MockOracle()
    for e in G.edges():
        oracle.values[e] = 1.0
        oracle.grads[e] = 1.0

    net_oracle = NetworkOracle(gra, u, oracle)
    x: List[float] = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is None


def test_network_oracle_stress_with_negative_cycle() -> None:
    """Test with a large graph and a negative cycle."""
    num_nodes = 1000
    G = create_large_graph(num_nodes)
    gra: Dict[Any, Dict[Any, Any]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: List[float] = [0.0] * num_nodes
    oracle = MockOracle()
    for e in G.edges():
        oracle.values[e] = 1.0
        oracle.grads[e] = 1.0

    # Introduce a negative cycle
    oracle.values[(num_nodes - 1, 0)] = -float(num_nodes)

    net_oracle = NetworkOracle(gra, u, oracle)
    x: List[float] = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is not None
