""" Import plotly helpers
"""
# flake8: noqa: F403,F401

__all__ = ["plotly"]

try:
    import plotly
except ImportError:
    plotly = None
else:
    import plotly.graph_objects as go
    import plotly.express as px

    from . import _subplots

    from ._subplots import *

    __all__ += _subplots.__all__ + [
        "go",
        "px",
    ]
