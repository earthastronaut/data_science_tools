""" Data Science Tools
"""
# flake8: noqa: F403,F401
from . import (
    config,
    dataframe,
    visualization,
    python_cli_tools,
    quantize,
    statistics,
    utils,
    weighted,
)

from .dataframe import *
from .visualization import *
from .python_cli_tools import *
from .quantize import *
from .statistics import *
from .utils import *
from .weighted import *

__version__ = "0.1.5"
__all__ = (
    [
        "config",
    ]
    + dataframe.__all__
    + visualization.__all__
    + python_cli_tools.__all__
    + quantize.__all__
    + statistics.__all__
    + utils.__all__
    + weighted.__all__
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
config.initialize()
