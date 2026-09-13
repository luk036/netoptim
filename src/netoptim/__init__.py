"""Network Flow Optimization Package.

Provides tools for solving parametric network flow problems
using cutting-plane methods and ellipsoid algorithms.
"""

from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from typing import Any, Optional, Tuple

from ellalgo.cutting_plane import cutting_plane_feas, cutting_plane_optim
from ellalgo.ell import Ell
from ellalgo.ell_config import Options

from .network_oracle import NetworkOracle
from .optscaling_oracle import OptScalingOracle

DEFAULT_TOLERANCE = 1e-8
"""Default convergence tolerance used by the solver facades.

Looser than :class:`ellalgo.ell_config.Options`' built-in ``1e-20``, which is
far below machine precision relative to typical objective magnitudes and only
inflates the iteration count. Pass an explicit ``Options`` to override.
"""

__all__ = [
    "NetworkOracle",
    "OptScalingOracle",
    "solve_network_feas",
    "solve_opt_scaling",
]


def _default_options() -> Options:
    options = Options()
    options.tolerance = DEFAULT_TOLERANCE
    return options


def solve_network_feas(
    oracle: NetworkOracle,
    space: Ell,
    options: Optional[Options] = None,
) -> Tuple[Optional[Any], int]:
    """Solve a parametric network feasibility problem.

    Facade that drives a :class:`NetworkOracle` through the ellipsoid
    cutting-plane method.

    Args:
        oracle: A feasibility oracle (typically a :class:`NetworkOracle`).
        space: The ellipsoid search space, whose center is the starting iterate.
        options: Algorithm control parameters. Defaults to an :class:`Options`
            with :data:`DEFAULT_TOLERANCE`.

    Returns:
        ``(x_best, num_iters)`` as returned by
        :func:`ellalgo.cutting_plane.cutting_plane_feas`.
    """
    return cutting_plane_feas(oracle, space, options or _default_options())


def solve_opt_scaling(
    oracle: OptScalingOracle,
    space: Ell,
    gamma: float,
    options: Optional[Options] = None,
) -> Tuple[Optional[Any], float, int]:
    """Solve an optimal-matrix-scaling problem.

    Facade that drives a :class:`OptScalingOracle` through the ellipsoid
    cutting-plane method.

    Args:
        oracle: An optimality oracle (typically a :class:`OptScalingOracle`).
        space: The ellipsoid search space.
        gamma: Initial best-so-far objective value.
        options: Algorithm control parameters. Defaults to an :class:`Options`
            with :data:`DEFAULT_TOLERANCE`.

    Returns:
        ``(x_best, value, num_iters)`` as returned by
        :func:`ellalgo.cutting_plane.cutting_plane_optim`.
    """
    return cutting_plane_optim(oracle, space, gamma, options or _default_options())
