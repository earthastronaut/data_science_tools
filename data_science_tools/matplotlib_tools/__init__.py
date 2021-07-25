""" Visualizations.
"""
# flake8: noqa: F403,F401

import os

try:
    import matplotlib
    import pylab as plt
except ImportError:
    matplotlib = None
    plt = None

__all__ = ["plt", "matplotlib"]

DATA_SCIENCE_MPLSTYLE_FILEPATH = os.path.join(
    os.path.dirname(__file__), "resources/theme.mplstyle"
)

if matplotlib is not None:
    plt.style.use(DATA_SCIENCE_MPLSTYLE_FILEPATH)

    from . import (
        formatters,
        visualize,
    )

    from .formatters import *
    from .visualize import *

    __all__ += formatters.__all__ + visualize.__all__
