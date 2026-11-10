from typing import Any, Dict

import numpy as np
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell
from pytest import approx

from netoptim.css_oracle import ClockScheduleOracle


def _acyclic_two_node_graph() -> Dict[str, Dict[str, Dict[str, Any]]]:
    return {"v0": {"v1": {"type": "s", "delay": 1.0}}, "v1": {}}


def _clock_oracle() -> ClockScheduleOracle:
    graph = _acyclic_two_node_graph()
    dist: Dict[str, float] = {v: 0.0 for v in graph}
    return ClockScheduleOracle(graph, dist)


def test_assess_optim_negative_tcp() -> None:
    oracle = _clock_oracle()
    tcp = -1.5
    cut, value = oracle.assess_optim(np.array([tcp, 1.0]), 1.0)
    assert value is None
    assert np.array_equal(cut[0], np.array([-1.0, 0.0]))
    assert cut[1] == -tcp


def test_assess_optim_nonpositive_beta() -> None:
    oracle = _clock_oracle()
    for beta in (0.0, -2.0):
        cut, value = oracle.assess_optim(np.array([2.0, beta]), 1.0)
        assert value is None
        assert np.array_equal(cut[0], np.array([0.0, -1.0]))
        assert cut[1] == -beta


def test_minimize_ratio() -> None:
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v0": {"v3": {"type": "s", "delay": 6.0}, "v2": {"type": "s", "delay": 7.0}},
        "v1": {"v2": {"type": "s", "delay": 9.0}, "v4": {"type": "h", "delay": 3.0}},
        "v2": {
            "v0": {"type": "h", "delay": 6.0},
            "v1": {"type": "h", "delay": 6.0},
            "v3": {"type": "s", "delay": 6.0},
        },
        "v3": {
            "v4": {"type": "s", "delay": 8.0},
            "v0": {"type": "h", "delay": 6.0},
            "v2": {"type": "h", "delay": 6.0},
        },
        "v4": {"v1": {"type": "s", "delay": 3.0}, "v3": {"type": "h", "delay": 8.0}},
    }

    xinit = np.array([7.5, 1.0])
    ellip = Ell(100.0, xinit)
    dist: Dict[str, float] = {v: 0.0 for v in digraph}
    omega = ClockScheduleOracle(digraph, dist)
    xbest, ratio, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None
    assert ratio == approx(3.040717067415985)
