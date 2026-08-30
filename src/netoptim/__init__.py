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

from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell

from ._typing import Cut
from .network_oracle import NetworkOracle
from .optscaling_oracle import OptScalingOracle

__all__ = ["NetworkOracle", "OptScalingOracle", "solve_network_feas", "solve_opt_scaling"]


def solve_network_feas(
    oracle: NetworkOracle, space: Ell, x0: Any
) -> Tuple[Optional[Any], float, int]:
    """Solve a parametric network feasibility problem.

    Facade that drives a :class:`NetworkOracle` through the ellipsoid
    cutting-plane method.

    Args:
        oracle: A feasibility oracle (typically a :class:`NetworkOracle`).
        space: The ellipsoid search space.
        x0: Initial iterate for the cutting-plane search.

    Returns:
        ``(x_best, value, num_iters)`` as returned by
        :func:`ellalgo.cutting_plane.cutting_plane_optim`.
    """
    return cutting_plane_optim(oracle, space, x0)


def solve_opt_scaling(
    oracle: OptScalingOracle, space: Ell, gamma: float
) -> Tuple[Optional[Any], float, int]:
    """Solve an optimal-matrix-scaling problem.

    Facade that drives a :class:`OptScalingOracle` through the ellipsoid
    cutting-plane method.

    Args:
        oracle: An optimality oracle (typically a :class:`OptScalingOracle`).
        space: The ellipsoid search space.
        gamma: Initial best-so-far objective value.

    Returns:
        ``(x_best, value, num_iters)`` as returned by
        :func:`ellalgo.cutting_plane.cutting_plane_optim`.
    """
    return cutting_plane_optim(oracle, space, gamma)
