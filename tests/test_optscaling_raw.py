from math import exp, log

import numpy as np

# from digraphx.tiny_digraph import DiGraphAdapter
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell
from mywheel.map_adapter import MapAdapter

from netoptim.optscaling_oracle import OptScalingOracle


def get_cost(edge):
    return edge


def test_optscaling_raw():
    """[summary]

    Keyword Arguments:
        duration (float): [description] (default: {0.000001})

    Returns:
        [type]: [description]

    A = [[ 0,  0, 22, 16, 15],
         [ 0, 10, 20, 14,  0],
         [125, 19, 13,  0,  0],
         [18, 12,  0,  0, 24],
         [11, 21,  0, 23, 17]]
    """

    gra = MapAdapter(
        [
            {
                2: (log(22.0), log(125.0)),
                3: (log(16.0), log(18.0)),
                4: (log(15.0), log(11.0)),
            },
            {
                1: (log(10.0), log(10.0)),
                2: (log(20.0), log(19.0)),
                3: (log(14.0), log(12.0)),
                4: (100, log(21.0)),
            },
            {
                0: (log(125.0), log(22.0)),
                1: (log(19.0), log(20.0)),
                2: (log(13.0), log(13.0)),
            },
            {
                0: (log(18.0), log(16.0)),
                1: (log(12.0), log(14.0)),
                4: (log(24.0), log(23.0)),
            },
            {
                0: (log(11.0), log(15.0)),
                1: (log(21.0), -100),
                3: (log(23.0), log(24.0)),
                4: (log(17.0), log(17.0)),
            },
        ]
    )
    # lst = [cost for item in gra.values() for (cost, _) in item.values()]
    # cmax = max(lst)
    # cmin = min(lst)
    cmax = log(125.0)
    cmin = log(10.0)
    xinit = np.array([cmax, cmin])
    t = cmax - cmin
    ellip = Ell(200 * t, xinit)
    dist = list(0.0 for _ in gra)
    omega = OptScalingOracle(gra, dist, get_cost)
    xbest, f, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None
    print(exp(xbest[0]), exp(xbest[1]))
    mindist = min(dist)
    dist = [i - mindist for i in dist]
    print([exp(i) for i in dist])
    print(exp(f))


def test_optscaling_raw2():
    """[summary]

    Keyword Arguments:
        duration (float): [description] (default: {0.000001})

    Returns:
        [type]: [description]

    A = [[ 0,  0, 22,  0,  0],
         [ 0,  0,  0,  0,  0],
         [25,  0,  0,  0,  0],
         [ 0,  0,  0,  0,  0],
         [ 0, 28,  0,  0,  0]]
    """

    gra = MapAdapter(
        [
            {
                2: (log(22.0), log(25.0)),
            },
            {
                4: (100, log(28.0)),
            },
            {
                0: (log(25.0), log(22.0)),
            },
            {},
            {
                1: (log(28.0), -100),
            },
        ]
    )
    # lst = [cost for item in gra.values() for (cost, _) in item.values()]
    # cmax = max(lst)
    # cmin = min(lst)
    cmax = log(28.0)
    cmin = log(22)
    xinit = np.array([cmax, cmin])
    t = cmax - cmin
    ellip = Ell(200 * t, xinit)
    dist = list(0.0 for _ in gra)
    omega = OptScalingOracle(gra, dist, get_cost)
    xbest, f, _ = cutting_plane_optim(omega, ellip, float("inf"))
    assert xbest is not None
    print(exp(xbest[0]), exp(xbest[1]))
    print([exp(i) for i in dist])
    print(exp(f))
