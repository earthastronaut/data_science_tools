""" Figure subplot for plotly

Made this semi-private because there is plotly.subplots
"""
import functools

from typing import Dict, Union

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


__all__ = [
    'FigureSubplot',
]


def placeholder(*args, **kwargs): # pylint: disable=unused-argument
    """ Placeholder to appease the linting gods """


class FigureSubplot:
    """ Plotly subplot is an axes of a figure

    Methods of the subplot will use the figure.{method} but inject
    parameters like row and col where necessary to select the specific
    subplot.

    """
    # These are overwritten but useful for linters to know
    add_trace = placeholder
    add_scatter = placeholder
    add_histogram = placeholder
    update_xaxes = placeholder
    update_yaxes = placeholder

    def __init__(
            self,
            figure: Union[Dict, go.Figure] = None,
            row: int = 1,
            col: int = 1,
            secondary_y: bool = False
    ):
        if figure is None:
            figure = make_subplots(rows=1, cols=1)
        elif isinstance(figure, dict):
            figure = make_subplots(**figure)

        self.figure = figure
        self.subplot = figure.get_subplot(row, col)

        self.row = row
        self.col = col
        self.secondary_y = secondary_y

        row_col = ['row', 'col']
        row_col_secondary_y = row_col + ['secondary_y']

        wrap_figure_methods = {
            'add_trace': {
                'wrap_kws': row_col_secondary_y,
            },
            'add_scatter': {
                'wrap_kws': row_col_secondary_y,
                'wrap_y_series': True,
            },
            'add_histogram': {
                'wrap_kws': row_col_secondary_y,
            },
            'update_xaxes': {
                'wrap_kws': row_col,
            },
            'update_yaxes': {
                'wrap_kws': row_col,
            },
        }

        for method_name, kws in wrap_figure_methods.items():
            func = self._wrapped_figure_method(method_name, *kws['wrap_kws'])
            if kws.get('wrap_y_series', False):
                func = self._wrap_y_series(func)
            setattr(self, method_name, func)

    @staticmethod
    def _wrap_y_series(method: callable):
        """ Wraps the function so if y is a pandas Series then it will
        convert y series to x=y.index and y=y.values and name=y.name
        """
        @functools.wraps(method)
        def wrapped(*args, **kws):
            possible_series = kws.get('y', None)
            if isinstance(possible_series, pd.Series):
                kws['x'] = possible_series.index.values
                kws['y'] = possible_series.values
                kws.setdefault('name', possible_series.name)
            return method(*args, **kws)
        return wrapped

    def _wrapped_figure_method(self, method_name: str, *keywords):
        """ Take the method from the self.figure and overwrite keywords
        with attributes from this object
        """
        method = getattr(self.figure, method_name)

        @functools.wraps(method)
        def wrapped(*args, **kws):
            for key in keywords:
                kws.setdefault(key, getattr(self, key))
            return method(*args, **kws)
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
    fig.add_trace(go.Scatter(x=x, y=y+0.5), row=2, col=1)
    ax.add_scatter(x=x, y=y-0.5)
    ax.add_scatter(y=pd.Series(y-0.8, index=x, name='series'))
    ax.update_xaxes(title='Hello X')
    ax.update_yaxes(title='Hello Y')

    fig.show()
