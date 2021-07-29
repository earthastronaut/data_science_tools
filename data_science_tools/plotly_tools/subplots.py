""" Figure subplot for plotly

Made this semi-private because there is plotly.subplots
"""
# standard
import functools
import inspect
from typing import Union, Tuple, List, Dict
from collections.abc import Callable

# external
import plotly
import plotly.graph_objects as go
import numpy as np
import numpy.typing  # pylint: disable=import-error,no-name-in-module

# internal
from .types import TFigure

__all__ = [
    "FigureSubplot",
]

BaseTypes = Union[str, bool, float, int]


def placeholder(*args, **kwargs):  # pylint: disable=unused-argument
    """Placeholder to appease the linting gods"""


class FigureSubplot(go.Figure):
    """Pass through Figure.<method> wrapping row, col, secondary_y as
    parameters
    """

    def __init__(
        self,
        figure: TFigure = None,
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


def _get_row_cols(
    rows: int = None,
    cols: int = None,
    subplot_count: int = None,
) -> Tuple[int, int]:
    """Get rows and cols with defaults"""
    if subplot_count:
        subplot_count = int(subplot_count)
        if rows is None and cols is None:
            raise ValueError("must specify either rows or cols with subplot_count")
        elif rows is not None and cols is not None:
            raise ValueError("must not specify all rows, cols, subplot_count")
        elif rows is None and cols is not None:
            rows = np.ceil(subplot_count / cols)
        elif rows is not None and cols is None:
            cols = np.ceil(subplot_count / rows)
    if rows is None:
        rows = 1
    if cols is None:
        cols = 1
    return rows, cols


def _convert_figure_to_subplots(
    figure: go.Figure,
) -> numpy.typing.NDArray[FigureSubplot]:
    """Take the figure grid ref and convert to array"""
    grid_ref = figure._grid_ref  # pylint: disable=protected-access
    row_subplots = []
    for row_i, row in enumerate(grid_ref):
        col_subplots = []
        for col_i, col in enumerate(row):
            secondary_subplots = []
            for secondary_i, _ in enumerate(col):
                if secondary_i > 1:
                    raise Exception("Unknown extra subplot")
                secondary_y_subplot = secondary_i == 1
                secondary_subplots.append(
                    FigureSubplot(
                        figure,
                        row=row_i + 1,
                        col=col_i + 1,
                        secondary_y=secondary_y_subplot,
                    )
                )
            col_subplots.append(secondary_subplots)
        row_subplots.append(col_subplots)
    subplots = np.array(row_subplots)
    return subplots


def make_subplots(
    rows: int = None,
    cols: int = None,
    subplot_count: int = None,
    secondary_y: bool = False,
    shared_xaxes: Union[bool, str] = False,
    shared_yaxes: Union[bool, str] = False,
    start_cell: str = "top-left",
    print_grid: bool = False,
    horizontal_spacing: float = None,
    vertical_spacing: float = None,
    subplot_titles: List[str] = None,
    column_widths: List[float] = None,
    column_width: int = 400,
    row_heights: List[float] = None,
    row_height: int = 400,
    specs: List[List[Dict[str, BaseTypes]]] = None,
    insets: List[List[Dict[str, BaseTypes]]] = None,
    column_titles: List[str] = None,
    row_titles: List[str] = None,
    x_title: str = None,
    y_title: str = None,
    figure: go.Figure = None,
    **kws,
) -> numpy.typing.NDArray[FigureSubplot]:
    """Make subplots with FigureSubplot objects

    Returns:
        NDArray[FigureSubplot]: A grid of the subplots.
            ndim: 3
            shape: (rows, cols, secondary_axes)
    """
    rows, cols = _get_row_cols(
        rows=rows,
        cols=cols,
        subplot_count=subplot_count,
    )

    kws.update(
        rows=rows,
        cols=cols,
        shared_xaxes=shared_xaxes,
        shared_yaxes=shared_yaxes,
        start_cell=start_cell,
        print_grid=print_grid,
        horizontal_spacing=horizontal_spacing,
        vertical_spacing=vertical_spacing,
        subplot_titles=subplot_titles,
        column_widths=column_widths,
        row_heights=row_heights,
        specs=specs,
        insets=insets,
        column_titles=column_titles,
        row_titles=row_titles,
        x_title=x_title,
        y_title=y_title,
        figure=figure,
    )

    if secondary_y:
        specs = kws["specs"] or []
        for i in range(rows):
            if i >= len(specs):
                specs.append([])
            for j in range(cols):
                if j >= len(specs[i]):
                    specs[i].append({"secondary_y": True})
                else:
                    specs[i][j]["secondary_y"] = True
        kws["specs"] = specs

    if kws.get("shared_xaxes", False):
        kws["vertical_spacing"] = kws.get("vertical_spacing") or 0.01

    figure = plotly.subplots.make_subplots(**kws)
    subplots = _convert_figure_to_subplots(figure)
    layout: Dict[str, BaseTypes] = {}
    if column_width is None:
        layout["width"] = column_width * subplots.shape[1]
    if row_height is None:
        layout["height"] = row_height * subplots.shape[0]
    figure.update_layout(**layout)
    return subplots


make_subplots.__doc__ += plotly.subplots.make_subplots.__doc__


# if __name__ == "__main__":
#     import numpy as np
#     x = np.arange(-10, 10, 0.2)
#     y = np.sin(x)
#     fig = make_subplots(2, 1)
#     ax = FigureSubplot(fig, 1, 1)
#     ax.add_trace(go.Scatter(x=x, y=y))
#     ax = FigureSubplot(fig, 2, 1)
#     ax.add_trace(go.Scatter(x=x, y=y))
#     fig.add_trace(go.Scatter(x=x, y=y + 0.5), row=2, col=1)
#     ax.add_scatter(x=x, y=y - 0.5)
#     ax.add_scatter(y=pd.Series(y - 0.8, index=x, name="series"))
#     ax.update_xaxes(title="Hello X")
#     ax.update_yaxes(title="Hello Y")
#     fig.show()
