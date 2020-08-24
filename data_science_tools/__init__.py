""" Data Science Tools
"""
from . import (
    config,
    dataframe,
    visualization,
    quantize,
    utils,
    weighted,
)

from .dataframe import *
from .visualization import *
from .quantize import *
from .utils import *
from .weighted import *

__version__ = '0.1.1'
__all__ = (
    [
        'config',
    ]
    + dataframe.__all__
    + visualization.__all__
    + quantize.__all__
    + utils.__all__
    + weighted.__all__
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
config.initialize()
