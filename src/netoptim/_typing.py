"""Shared type definitions for the netoptim oracles.

Centralises the structural contract for the edge-level oracle used by the
oracle classes, plus the cutting-plane type alias.
"""

from typing import Any, Protocol, Tuple


class EdgeOracle(Protocol):
    """Structural contract for an edge-level oracle.

    Implementations provide ``eval`` and ``grad`` for a single edge at a given
    iterate ``x``; ``update`` is an optional hook.

    An implementation MAY also provide ``make_weight_fn(x)``, a factory that
    returns a callable ``edge -> weight`` with the iterate's scalars bound once.
    :class:`~netoptim.network_oracle.NetworkOracle` uses it when present to
    avoid re-indexing ``x`` on every edge in the hot loop.
    """

    def eval(self, edge: Any, x: Any) -> Any: ...

    def grad(self, edge: Any, x: Any) -> Any: ...

    def update(self, t: Any) -> None: ...


Cut = Tuple[Any, float]
"""A cutting plane: (gradient, intercept)."""
