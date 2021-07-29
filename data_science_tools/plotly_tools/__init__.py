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

    from . import subplots

    from .subplots import *

    __all__ += subplots.__all__ + [
        "go",
        "plotly",
        "px",
    ]
