""" Data Science Tools
"""
# flake8: noqa: F403,F401
from . import config


def get_version():
    """Get version number"""
    # TODO: remove the redefine-outer-name when removing *
    import os  # pylint: disable=redefined-outer-name,import-outside-toplevel

    with open(os.path.join(os.path.dirname(__file__), "__version__")) as buffer:
        return buffer.readline().strip()


__version__ = get_version()
__all__ = ["config", "__version__"]

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

config.initialize()
