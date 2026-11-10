from typing import Any, Dict, List, Tuple, Union

import networkx as nx
import numpy as np
from ellalgo.ell import Ell
from ellalgo.ell_config import Options

from netoptim import solve_network_feas
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


class HookOracle(MockOracle):
    """Oracle exposing the optional ``make_weight_fn`` fast path."""

    def __init__(self) -> None:
        super().__init__()
        self.prepare_calls = 0

    def make_weight_fn(self, x: List[float]):
        self.prepare_calls += 1
        values = self.values

        def weight(edge: Tuple[Any, Any]) -> float:
            return values.get(edge, 0.0)

        return weight


def test_network_oracle_update() -> None:
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra: Dict[Any, Dict[Any, Union[Dict[str, Any], Tuple[Any, Any]]]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: Dict[Any, float] = {0: 0.0, 1: 0.0, 2: 0.0}
    oracle = MockOracle()
    net_oracle = NetworkOracle(gra, u, oracle)
    net_oracle.update(1.0)
    assert oracle.t == 1.0


def test_network_oracle_assess_feas_with_negative_cycle() -> None:
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra: Dict[Any, Dict[Any, Union[Dict[str, Any], Tuple[Any, Any]]]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: Dict[Any, float] = {0: 0.0, 1: 0.0, 2: 0.0}
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
    gra: Dict[Any, Dict[Any, Union[Dict[str, Any], Tuple[Any, Any]]]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    u: Dict[Any, float] = {0: 0.0, 1: 0.0, 2: 0.0}
    oracle = MockOracle()
    oracle.values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): 1.0}
    net_oracle = NetworkOracle(gra, u, oracle)
    x: List[float] = [0.0]
    cut = net_oracle.assess_feas(x)
    assert cut is None


def test_network_oracle_uses_make_weight_fn() -> None:
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra: Dict[Any, Dict[Any, Union[Dict[str, Any], Tuple[Any, Any]]]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): -3.0}
    grads = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): -1.0}

    plain = MockOracle()
    plain.values = dict(values)
    plain.grads = dict(grads)
    cut_plain = NetworkOracle(gra, {0: 0.0, 1: 0.0, 2: 0.0}, plain).assess_feas([0.0])

    hooked = HookOracle()
    hooked.values = dict(values)
    hooked.grads = dict(grads)
    cut_hooked = NetworkOracle(gra, {0: 0.0, 1: 0.0, 2: 0.0}, hooked).assess_feas([0.0])

    assert hooked.prepare_calls == 1
    assert cut_hooked is not None
    assert cut_hooked == cut_plain


def test_solve_network_feas_returns_feasible_point() -> None:
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    gra: Dict[Any, Dict[Any, Union[Dict[str, Any], Tuple[Any, Any]]]] = {
        u: {v: (u, v) for v in G.neighbors(u)} for u in G.nodes()
    }
    oracle = MockOracle()
    oracle.values = {(0, 1): 1.0, (1, 2): 1.0, (2, 0): 1.0}
    net_oracle = NetworkOracle(gra, {0: 0.0, 1: 0.0, 2: 0.0}, oracle)
    space = Ell(10.0, np.array([0.0, 0.0]))

    x_best, niter = solve_network_feas(net_oracle, space)

    assert x_best is not None
    assert niter == 0


def test_network_oracle_picks_most_critical_cycle() -> None:
    gra: Dict[Any, Dict[Any, Any]] = {
        0: {1: (0, 1)},
        1: {0: (1, 0)},
        2: {3: (2, 3)},
        3: {2: (3, 2)},
    }
    oracle = MockOracle()
    oracle.values = {(0, 1): -1.0, (1, 0): -1.0, (2, 3): -5.0, (3, 2): 0.0}
    oracle.grads = {(0, 1): -1.0, (1, 0): -1.0, (2, 3): -1.0, (3, 2): -1.0}
    net_oracle = NetworkOracle(gra, {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}, oracle)

    cut = net_oracle.assess_feas([0.0])

    assert cut is not None
    g, f = cut
    assert g == 2.0
    assert f == 5.0


def test_network_oracle_empty_or_disconnected_graph() -> None:
    oracle = MockOracle()
    x: List[float] = [0.0]
    empty: Dict[Any, Dict[Any, Any]] = {}
    assert NetworkOracle(empty, {}, oracle).assess_feas(x) is None
    no_edges: Dict[Any, Dict[Any, Any]] = {0: {}, 1: {}}
    assert NetworkOracle(no_edges, {0: 0.0, 1: 0.0}, oracle).assess_feas(x) is None


def test_solve_network_feas_forwards_options() -> None:
    gra: Dict[Any, Dict[Any, Any]] = {0: {1: (0, 1)}, 1: {0: (1, 0)}}
    oracle = MockOracle()
    oracle.values = {(0, 1): -1.0, (1, 0): -1.0}
    oracle.grads = {
        (0, 1): np.array([-1.0, -1.0]),
        (1, 0): np.array([-1.0, -1.0]),
    }
    net_oracle = NetworkOracle(gra, {0: 0.0, 1: 0.0}, oracle)
    space = Ell(10.0, np.array([0.0, 0.0]))
    options = Options()
    options.max_iters = 1

    x_best, niter = solve_network_feas(net_oracle, space, options)

    assert x_best is None
    assert niter == 1
