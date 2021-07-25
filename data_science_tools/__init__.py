""" Data Science Tools
"""
# flake8: noqa: F403,F401
from . import (
    config,
    dataframe,
    visualization,
    python_interactive,
    quantize,
    statistics,
    jupyter,
    utils,
    weighted,
)

from .dataframe import *
from .visualization import *
from .python_interactive import *
from .quantize import *
from .statistics import *
from .utils import *
from .weighted import *


def get_version():
    """Get version number"""
    # import os TODO: update this from *

    with open(os.path.join(os.path.dirname(__file__), "__version__")) as buffer:
        return buffer.readline().strip()


__version__ = get_version()
__all__ = (
    [
        "config",
    ]
    + dataframe.__all__
    + visualization.__all__
    + python_interactive.__all__
    + quantize.__all__
    + statistics.__all__
    + utils.__all__
    + weighted.__all__
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
config.initialize()
