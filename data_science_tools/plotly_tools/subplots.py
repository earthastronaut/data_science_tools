""" Figure subplot for plotly

Made this semi-private because there is plotly.subplots
"""
# pylint: disable=too-many-locals

# standard
import functools
import inspect
import logging
from typing import Any, Union, Tuple, List, Dict
from collections.abc import Callable

# external
import plotly
import plotly.graph_objects as go
import numpy as np
import numpy.typing  # pylint: disable=import-error,no-name-in-module

# internal
from .types import TFigure

logger = logging.getLogger(__name__)

__all__ = [
    "FigureSubplot",
    "make_subplots",
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
            specs = _get_specs_updated(
                row,
                col,
                secondary_y=secondary_y,
            )
            fig = plotly.subplots.make_subplots(rows=row, cols=col, specs=specs)
        elif isinstance(figure, go.Figure):
            fig = figure
        else:
            raise TypeError(f"Invalid figure type {type(figure)}")

        super().__init__()
        for key, obj in fig.__dict__.items():
            if not callable(obj):
                self.__dict__[key] = obj

        self._figure = fig
        self._row = row
        self._col = col
        self._secondary_y = secondary_y
        self._array_index = (row - 1, col - 1, 1 if secondary_y else 0)
        i, j, k = self._array_index
        self._subplot_ref = fig._grid_ref[i][j][k]

        self._xaxis_ref = ""
        self._yaxis_ref = ""
        subplot_layout_keywords_rename = {}
        for key in self._subplot_ref.layout_keys:
            if key.startswith("xaxis"):
                self._xaxis_ref = key
                if key != "xaxis":
                    subplot_layout_keywords_rename["xaxis"] = key

            if key.startswith("yaxis"):
                self._yaxis_ref = key
                if key != "yaxis":
                    subplot_layout_keywords_rename["yaxis"] = key

        self._subplot_layout_keywords_rename = subplot_layout_keywords_rename

        self._init_wrap_figure_methods(
            row=self.row,
            col=self.col,
            secondary_y=self.secondary_y,
            # rows=(self.row,),
            # cols=(self.col,),
            # secondary_ys=(self.secondary_y,),
        )

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

    @property
    def xaxis_domain(self):
        """Get domain range including overlaying"""
        axis = self.layout[self._xaxis_ref]
        if axis.overlaying is not None:
            ref = axis.overlaying.replace("x", "xaxis")  # x5 > xaxis5
            return self.layout[ref].domain
        else:
            return axis.domain

    @property
    def yaxis_domain(self):
        """Get domain range including overlaying"""
        axis = self.layout[self._yaxis_ref]
        if axis.overlaying is not None:
            ref = axis.overlaying.replace("y", "yaxis")  # y5 > yaxis5
            return self.layout[ref].domain
        else:
            return axis.domain

    def update_layout(
        self, dict1: Dict[str, Any] = None, overwrite: bool = False, **kwargs
    ):
        """
        Update the properties of the figure's layout with a dict and/or with
        keyword arguments.

        This recursively updates the structure of the original
        layout with the values in the input dict / keyword arguments.

        Parameters
        ----------
        dict1 : dict
            Dictionary of properties to be updated
        overwrite: bool
            If True, overwrite existing properties. If False, apply updates
            to existing properties recursively, preserving existing
            properties that are not specified in the update operation.
        kwargs :
            Keyword/value pair of properties to be updated

        Returns
        -------
        FigureSubplot
            The Figure object that the update_layout method was called on
        """
        kws = dict1 or {}
        kws.update(kwargs)

        rename = self._subplot_layout_keywords_rename

        title_kws = dict()
        for key in tuple(kws):
            if key.startswith("title"):
                value = kws.pop(key)
                if isinstance(value, dict):
                    title_kws.update(value)
                elif isinstance(value, str):
                    title_kws["text"] = value
                else:
                    title_kws[key] = value

            for key_to_rename, key_name_with in rename.items():
                if key.startswith(key_to_rename):
                    key_rename = key.replace(key_to_rename, key_name_with)
                    kws[key_rename] = kws.pop(key)
                    logger.debug(f"rename: {key} to {key_rename}")

        super().update_layout(kws, overwrite=overwrite)

        if len(title_kws):
            y = self.yaxis_domain[1]
            x = (self.xaxis_domain[1] + self.xaxis_domain[0]) * 0.5
            annotation_kws = dict(
                showarrow=False,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="bottom",
                y=y,
                x=x,
            )
            annotation_kws.update(title_kws)
            self._figure.add_annotation(**annotation_kws)

        return self

    @staticmethod
    def _get_new_signature(function: Callable, **defaults) -> inspect.Signature:
        """Get new defaults for function given the """
        try:
            sig = inspect.signature(function)
        except ValueError:
            return
        parameters = []
        for param in sig.parameters.values():
            if param.name in defaults:
                param = param.replace(default=defaults[param.name])
            parameters.append(param)
        return sig.replace(parameters=parameters)

    def _init_wrap_figure_methods(self, **defaults):
        """Initialize by wrapping"""
        for method_name in self._subplot_method_names(defaults.keys()):
            setattr(
                self, method_name, self._wrapped_figure_method(method_name, **defaults)
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

            method_keywords = set(sig.parameters.keys())
            if not len(method_keywords):
                continue

            if not method_keywords.isdisjoint(keywords_set):
                yield method_name

    def _wrapped_figure_method(self, method_name: str, **defaults):
        """Take the method from the self.figure and overwrite keywords
        with attributes from this object.
        """
        method = getattr(self, method_name)
        signature = self._get_new_signature(method, **defaults)

        kwargs = {
            key: value for key, value in defaults.items() if key in signature.parameters
        }

        @functools.wraps(method)
        def wrapper(*args, **kws):
            """wrapper"""
            kwargs.update(kws)
            return method(*args, **kwargs)

        wrapper.__doc__ = f"Subplot Wrapped: row={self.row} col={self.col} secondary_y={self.secondary_y}\n"  # noqa
        if method.__doc__:
            wrapper.__doc__ += method.__doc__
        wrapper.__signature__ = signature
        setattr(wrapper, "_is_wrapped_figure_method", True)
        return wrapper


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
    return int(rows), int(cols)


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


def _get_specs_updated(
    rows: int,
    cols: int,
    specs: List[List[Dict[str, BaseTypes]]] = None,
    secondary_y: bool = False,
) -> List[List[Dict[str, BaseTypes]]]:
    """Take the specs and update with the parameters"""
    specs_updated = []
    specs = specs or []
    ####################
    for i in range(rows):
        specs_updated.append([])
        ####################
        for j in range(cols):
            if i < len(specs) and j < len(specs[i]):
                spec = specs[i][j].copy()
            else:
                spec = {}
            spec["secondary_y"] = secondary_y
            specs_updated[i].append(spec)
    return specs_updated


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
        kws["specs"] = _get_specs_updated(
            rows,
            cols,
            specs=specs,
            secondary_y=secondary_y,
        )

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
