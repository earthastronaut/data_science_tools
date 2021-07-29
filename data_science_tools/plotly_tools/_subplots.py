""" Figure subplot for plotly

Made this semi-private because there is plotly.subplots
"""
# standard
import functools
import inspect
from typing import Optional, Tuple
from collections.abc import Callable

# external
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# internal
from .types import TFigure

__all__ = [
    "FigureSubplot",
]


def placeholder(*args, **kwargs):  # pylint: disable=unused-argument
    """Placeholder to appease the linting gods"""


class FigureSubplot(go.Figure):
    """Pass through Figure.<method> wrapping row, col, secondary_y as
    parameters
    """

    def __init__(
        self,
        figure: Optional[TFigure] = None,
        row: int = 1,
        col: int = 1,
        secondary_y: bool = False,
    ):
        if isinstance(figure, dict):
            fig = plotly.subplots.make_subplots(**figure)
        elif figure is None:
            fig = plotly.subplots.make_subplots(rows=1, cols=1)
        elif isinstance(figure, go.Figure):
            fig = figure
        else:
            raise TypeError(f"Invalid figure type {type(figure)}")

        super().__init__()
        for key, obj in fig.__dict__.items():
            if not callable(obj):
                self.__dict__[key] = obj

        self._row = row
        self._col = col
        self._secondary_y = secondary_y
        secondary = 1 if secondary_y else 0
        self._subplot_ref = fig._grid_ref[row - 1][col - 1][secondary]

        self._init_wrap_figure_methods(("row", "col"))
        self._init_wrap_figure_methods(("row", "col", "secondary_y"))
        self._init_wrap_figure_methods(("rows", "cols"))

    @property
    def figure(self):
        """Pass through for the figure of the subplot. """
        return self

    @property
    def subplot_ref(self):
        """Pass through for the figure of the subplot. """
        return self._subplot_ref

    @property
    def row(self):
        """Subplot row number. Figure has defined properties. """
        return self._row

    @property
    def col(self):
        """Subplot column number. Figure has defined properties. """
        return self._col

    @property
    def secondary_y(self):
        """Subplot secondary_y. Figure has defined properties. """
        return self._secondary_y

    rows = row
    cols = col
    # secondary_ys = secondary_y # not treated the same as the other two

    def _init_wrap_figure_methods(self, keywords: Tuple[str, ...]):
        """ Meant to be run once to wrape functions for these keywords """
        for method_name in self._subplot_method_names(keywords):
            setattr(
                self,
                method_name,
                self._wrapped_figure_method(getattr(self, method_name), keywords),
            )

    def _subplot_method_names(self, keywords: Tuple[str, ...]):
        """Iterate all methods which have subplot_keywords. """
        keywords_set = set(keywords)
        for method_name in dir(self):
            if method_name.startswith("_"):
                continue

            method = getattr(self, method_name)
            if not callable(method):
                continue

            is_wrapped_figure_method = getattr(
                method, "_is_wrapped_figure_method", False
            )
            if is_wrapped_figure_method:
                continue

            try:
                sig = inspect.signature(method)
            except ValueError:
                continue
            method_keywords = sig.parameters.keys()
            if set(method_keywords).issuperset(keywords_set):
                yield method_name

    def _wrapped_figure_method(self, method: Callable, keywords: Tuple[str, ...]):
        """Take the method from the self.figure and overwrite keywords
        with attributes from this object.
        """

        @functools.wraps(method)
        def wrapped(*args, **kws):
            for key in keywords:
                kws.setdefault(key, getattr(self, key))
            return method(*args, **kws)

        setattr(wrapped, "_is_wrapped_figure_method", True)
        return wrapped


if __name__ == "__main__":
    import numpy as np

    x = np.arange(-10, 10, 0.2)
    y = np.sin(x)

    fig = make_subplots(2, 1)
    ax = FigureSubplot(fig, 1, 1)
    ax.add_trace(go.Scatter(x=x, y=y))

    ax = FigureSubplot(fig, 2, 1)
    ax.add_trace(go.Scatter(x=x, y=y))
    fig.add_trace(go.Scatter(x=x, y=y + 0.5), row=2, col=1)
    ax.add_scatter(x=x, y=y - 0.5)
    ax.add_scatter(y=pd.Series(y - 0.8, index=x, name="series"))
    ax.update_xaxes(title="Hello X")
    ax.update_yaxes(title="Hello Y")

    fig.show()
