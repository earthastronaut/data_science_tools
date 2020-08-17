""" Data Science Tools
"""
from . import (
    config,
    visualization,
    quantize,
    utils,
)

from .visualization import *
from .quantize import *
from .utils import *

__version__ = '0.1.1'
__all__ = (
    [
        'config',
    ]
    + visualization.__all__
    + quantize.__all__
    + utils.__all__
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
config.initialize()
