"""Shared type definitions for the netoptim oracles.

Centralises the structural contract for the edge-level oracle used by the
oracle classes, plus the cutting-plane type alias.
"""

from typing import Any, Protocol, Tuple


class EdgeOracle(Protocol):
    """Structural contract for an edge-level oracle.

    Implementations provide ``eval`` and ``grad`` for a single edge at a given
    iterate ``x``; ``update`` is an optional hook.
    """

    def eval(self, edge: Any, x: Any) -> Any: ...

    def grad(self, edge: Any, x: Any) -> Any: ...

    def update(self, t: Any) -> None: ...


Cut = Tuple[Any, float]
"""A cutting plane: (gradient, intercept)."""
