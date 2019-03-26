"""
netoptim
=====
"""

from __future__ import absolute_import

import sys
if sys.version_info[:2] < (2, 7):
    m = "Python 2.7 or later is required for NetworkX (%d.%d detected)."
    raise ImportError(m % sys.version_info[:2])
del sys

# Release data
from netoptim import release

# from netoptim.oracles import *
from netoptim.neg_cycle import *
from netoptim.parametric import *
from netoptim.min_cycle_ratio import *

# from netoptim.lsq_corr_ell import lsq_corr_poly, lsq_corr_bspline
