"""Shared type definitions for the netoptim oracles.

Centralises the structural contract for the edge-level oracle used by the
oracle classes, plus the cutting-plane type alias.
"""

from typing import (
    Any,
    Callable,
    MutableMapping,
    MutableSequence,
    Protocol,
    Tuple,
    Union,
)

import numpy as np

Arr = np.ndarray
"""A NumPy array type alias for array operations in the optimization."""

Dist = Union[MutableMapping[Any, float], MutableSequence[float]]
"""Initial node potentials: either a mapping or an indexable sequence."""


class EdgeOracle(Protocol):
    """Structural contract for an edge-level oracle.

    Implementations provide ``eval`` and ``grad`` for a single edge at a given
    iterate ``x``, plus an ``update`` hook for the best-so-far value.
    """

    def eval(self, edge: Any, x: Any) -> float:
        """Evaluate the edge weight at iterate ``x``."""
        ...

    def grad(self, edge: Any, x: Any) -> Union[float, Arr]:
        """Return the subgradient of the edge weight at iterate ``x``."""
        ...

    def update(self, t: float) -> None:
        """Update the oracle with the best-so-far value ``t``."""
        ...


class FastEdgeOracle(EdgeOracle, Protocol):
    """Optional hot-loop hook: an oracle that can bind ``x`` once.

    An implementation of :class:`EdgeOracle` MAY additionally provide
    ``make_weight_fn``.  :class:`~netoptim.network_oracle.NetworkOracle` uses
    it when present to obtain a callable ``edge -> weight`` with the iterate's
    scalars bound once, avoiding re-indexing ``x`` on every edge in the hot
    loop.
    """

    def make_weight_fn(self, x: Any) -> Callable[[Any], float]:
        """Return a ``edge -> weight`` callable with ``x`` bound once."""
        ...


Cut = Tuple[Any, float]
"""A cutting plane: (gradient, intercept)."""

GRAD_RATIO = np.array([1.0, -1.0])
GRAD_PI = np.array([1.0, 0.0])
GRAD_PSI = np.array([0.0, -1.0])
