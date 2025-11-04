from typing import Any, Dict, List, Tuple

import networkx as nx
import numpy as np
from netoptim.network_oracle import NetworkOracle


class MyOracle:
    def __init__(
        self, values: Dict[Tuple[Any, Any], float], grads: Dict[Tuple[Any, Any], float]
    ):
        self.values = values
        self.grads = grads

    def eval(self, edge: Tuple[Any, Any], x: List[float]) -> float:
        return self.values.get(edge, 0.0)

    def grad(self, edge: Tuple[Any, Any], x: List[float]) -> float:
        return self.grads.get(edge, 0.0)

    def update(self, t: float) -> None:
        pass


def test_network_oracle_with_real_oracle():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra = {u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()}
    u = [0.0, 0.0, 0.0]
    values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): -3.0}
    grads = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): -1.0}
    oracle = MyOracle(values, grads)
    net_oracle = NetworkOracle(gra, u, oracle)
    x = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is not None
    g, f = cut
    assert f == 1.0
    np.testing.assert_allclose(g, np.array([-1.0]))


def test_network_oracle_no_negative_cycle_real_oracle():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra = {u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()}
    u = [0.0, 0.0, 0.0]
    values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): 1.0}
    grads = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): 1.0}
    oracle = MyOracle(values, grads)
    net_oracle = NetworkOracle(gra, u, oracle)
    x = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is None


def test_network_oracle_more_complex_graph():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    gra = {u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()}
    u = [0.0, 0.0, 0.0, 0.0]
    values = {(0, 1): 1.0, (1, 2): 1.0, (2, 3): 1.0, (3, 0): -4.0, (0, 2): 0.5}
    grads = {(0, 1): 1.0, (1, 2): 1.0, (2, 3): 1.0, (3, 0): -1.0, (0, 2): 1.0}
    oracle = MyOracle(values, grads)
    net_oracle = NetworkOracle(gra, u, oracle)
    x = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is not None
    g, f = cut
    assert f == 2.5
    np.testing.assert_allclose(g, np.array([-1.0]))


def test_network_oracle_gradient():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra = {u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()}
    u = [0.0, 0.0, 0.0]
    values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): -3.0}
    grads = {(0, 1): 2.0, (1, 2): 3.0, (2, 0): -4.0}
    oracle = MyOracle(values, grads)
    net_oracle = NetworkOracle(gra, u, oracle)
    x = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is not None
    g, f = cut
    assert f == 1.0
    np.testing.assert_allclose(g, np.array([-1.0]))
