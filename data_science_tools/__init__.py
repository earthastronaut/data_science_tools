from . import (
    config,
    visualization,
    quantize,
)

from .visualization import *
from .quantize import *

__version__ = '0.1.0'
__all__ = (
    [
        'config',
    ]
    + visualization.__all__
    + quantize.__all__
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
config.initialize()
