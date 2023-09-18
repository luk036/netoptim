from math import log

import numpy as np
from digraphx.lict import Lict

# from digraphx.tiny_digraph import DiGraphAdapter
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell

from netoptim.optscaling_oracle import OptScalingOracle


def get_cost(edge):
    return edge


def test_optscaling_raw():
    """[summary]

    Keyword Arguments:
        duration (float): [description] (default: {0.000001})

    Returns:
        [type]: [description]
    """
    gra = Lict(
        [
            {1: (log(7.0), log(8.0)), 2: (log(5.0), log(4.0))},
            {0: (log(8.0), log(7.0)), 2: (log(3.0), log(2.0))},
            {0: (log(4.0), log(5.0)), 1: (log(2.0), log(3.0))},
        ]
    )
    lst = [cost for item in gra.values() for (cost, _) in item.values()]
    cmax = max(lst)
    cmin = min(lst)
    print(cmax, cmin)
    xinit = np.array([cmax, cmin])
    t = cmax - cmin
    ellip = Ell(1.5 * t, xinit)
    dist = list(0.0 for _ in gra)
    omega = OptScalingOracle(gra, dist, get_cost)
    xbest, _, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None
    print(log(xbest[0]), log(xbest[1]))
