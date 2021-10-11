""" Plotting functions
"""

# external
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# internal
from ._colors import format_color

__all__ = [
    "figure_with_traces",
    "plot_scatter_filled",
    "plot_dataframe",
]


def figure_with_traces(traces, figure=True):
    """Create or use figure and add traces/shapes

    Utility which takes a set of traces and returns a figure or passthrough traces
    for another figure later.

    Parameters
    ----------
    traces (List[go.Trace, go.Shape]): objects to add to a figure
    figure (True, False, go.Figure):
        True: create a new figure and return figure
        False: return traces
        go.Figure: use this figure and add traces

    Returns
    -------
    go.Figure or List[go.Trace, go.Shape]
    """
    if figure is False:
        return traces
    elif not isinstance(figure, go.Figure):
        figure = go.Figure()
    for obj in traces:
        if isinstance(obj, go.layout.Shape):
            figure.add_shape(obj)
        else:
            figure.add_trace(obj)
    return figure


def _kws_extract(prefix, **kws):
    extracted = {}
    keys = list(kws)
    for key in keys:
        if key.startswith(prefix):
            n_prefix = len(prefix)
            subkey = key[n_prefix:]
            extracted[subkey] = kws.pop(key)
    return extracted, kws


def _plot_scatter_upper(upper_x, upper_y, name, fillcolor=None, **kws_upper):
    # upper_x = x if upper_x is None else upper_x
    # upper_y = upper_y + y if is_relative_to_y else upper_y
    if isinstance(upper_y, (int, float)):
        upper_y = np.repeat(upper_y, len(upper_x))

    # UPPER
    kwargs_upper = dict(
        mode="lines",
        line_width=0,
        name=f"Upper Bound {name}",
        showlegend=False,
    )
    if fillcolor is not None:
        kwargs_upper.update(
            fillcolor=fillcolor,
            fill="tonexty",
        )
    kwargs_upper.update(kws_upper or {})
    kwargs_upper.update(
        x=upper_x,
        y=upper_y,
    )
    return go.Scatter(**kwargs_upper)


def _plot_scatter_lower(lower_x, lower_y, name, fillcolor, **lower_kws):
    if isinstance(lower_y, (int, float)):
        lower_y = np.repeat(lower_y, len(lower_x))

    # LOWER
    kwargs_lower = dict(
        mode="lines",
        line_width=0,
        fillcolor=fillcolor,
        fill="tonexty",
        name=f"Lower Bound {name}",
        showlegend=False,
    )
    kwargs_lower.update(lower_kws or {})
    kwargs_lower.update(
        x=lower_x,
        y=lower_y,
    )
    return go.Scatter(**kwargs_lower)


def _plot_scatter_center(x, y, **kws):
    kwargs = dict(
        mode="lines",
    )
    kwargs.update(kws)
    kwargs["x"] = x
    kwargs["y"] = y
    return go.Scatter(**kwargs)


def plot_scatter_filled(  # pylint: disable=too-many-locals
    x=None,
    y=None,
    lower_x=None,
    lower_y=None,
    upper_x=None,
    upper_y=None,
    df=None,
    relative=False,
    figure=True,
    fill_color=None,
    fill_opacity=0.1,
    name="",
    line_color="#067BFF",
    **kws,
):
    """Plot a shaded region of 3 lines: mid, lower, upper.

    https://plotly.com/python/continuous-error-bars/


    Parameters:
        x (array): Values of the mid x data
        y (array): Values of the mid y data
        lower_x (array): Values of the lower x data
        ...
        kws_upper (dict): keyword arguments to overwrite the upper go.Scatter line
        lower_kws (dict): keyword arguments to overwrite the lower go.Scatter line.
            This contains fill_color.
        relative: if True then will add y to the lower_y and upper_y values
        figure: If None, then will return traces. Else CREATE_FIGURE will create a
            figure. Otherwise, it'll use this figure to add the traces too.
        line_color: Color of the line, also default for fill_color
        fill_color: Color of the fill, default is the line_color.
        fill_opacity: Shading for the fill color.
        **kws: passed to the mid go.Scatter(**kws) as overwrites to the defaults.

    Returns:
        Figure: Returns a figure if figure is not None.
        or
        List[Scatter, Scatter, Scatter]: mid, upper, lower scatter traces respectively.

    """
    if df is not None:
        x = df.index if x is None else df[x]
        name = y or ""
        y = None if y is None else df[y]
        lower_y = None if lower_y is None else df[lower_y]
        upper_y = None if upper_y is None else df[upper_y]
        kws.setdefault("name", name)

    if x is None:
        if isinstance(y, (pd.Series)):
            x = y.index
        elif y is not None:
            x = range(len(y))
        else:
            raise TypeError("Could not determine x or y")

    upper_kws, center_kws = _kws_extract("upper_", **kws)
    lower_kws, center_kws = _kws_extract("lower_", **center_kws)

    traces = []
    if y is not None:
        kws.setdefault("line_color", line_color)
        center = _plot_scatter_center(x=x, y=y, **center_kws)
        line_color = center.line.color or line_color
        traces.append(center)

    if fill_color is None:
        fillcolor = format_color(line_color, alpha=fill_opacity)
    else:
        fillcolor = format_color(fill_color, alpha=fill_opacity)

    if upper_y is not None:
        traces.append(
            _plot_scatter_upper(
                upper_x=x if upper_x is None else upper_x,
                upper_y=upper_y + y if relative else upper_y,
                name=name,
                fillcolor=fillcolor if lower_y is None else None,
                **upper_kws,
            )
        )

    if lower_y is not None:
        traces.append(
            _plot_scatter_lower(
                lower_x=x if lower_x is None else lower_x,
                lower_y=lower_y + y if relative else lower_y,
                name=name,
                fillcolor=fillcolor,
                **lower_kws,
            )
        )

    return figure_with_traces(traces, figure=figure)


def _get_x_from_dataframe(df, x=None):
    # add x
    if x is None:
        return df.index
    elif isinstance(x, (list, tuple, np.ndarray, pd.Series)):
        return x
    else:
        return df[x]


def _get_y_from_dataframe(df, y=None):
    # add y
    if y is None:
        y_names = df.columns
    elif isinstance(y, list):
        y_names = y
    else:
        try:
            if y in df:
                y_names = [y]
        except TypeError:
            return {"": y}
    y_data = {}
    for name in y_names:
        y_data[name] = df[name]
    return y_data


def _get_kws_from_dataframe(y_names, **kws):
    # pd.DataFrame:
    #   index: y column names
    #   columns: kws
    input_df_kws = kws.pop("df_kws", None)
    if input_df_kws is None:
        df_kws = pd.DataFrame(index=y_names)
    elif isinstance(input_df_kws, pd.DataFrame):
        df_kws = input_df_kws.reindex(index=y_names)
    elif isinstance(input_df_kws, dict):
        df_kws = pd.DataFrame(index=y_names)
        for name, val in input_df_kws.items():
            if isinstance(val, dict):
                (value_flat,) = pd.json_normalize(val, sep="_").to_dict(
                    orient="records"
                )
                for column, value in value_flat.items():
                    df_kws.loc[name, column] = value
            else:
                TypeError(f"{name} {type(val)}")
    else:
        raise TypeError(str(type(input_df_kws)))

    (kws_flattened,) = pd.json_normalize(kws, sep="_").to_dict(orient="records")
    for key, value in kws_flattened.items():
        if key in df_kws:
            df_kws[key].fillna(value, inplace=True)
        else:
            df_kws[key] = value
    return df_kws


def _get_plot_obj(x_data, y_data, name, obj_class, **kwargs):
    y_column = y_data[name]
    obj_kws = dict(
        x=x_data,
        y=y_column,
        name=name,
    )
    obj_kws.update(kwargs)

    obj = obj_class(**obj_kws)
    return obj


def plot_dataframe(df, x=None, y=None, figure=True, go_class="Scatter", **kws):
    """Plot dataframes

    Parameters
    ----------
    df (pd.DataFrame): Base dataframe to build from
    x (None or hashable or array):
        None: uses df.index
        hashable: uses df[x]
        array: uses pd.Series(x, df.index)
    y (None or List[hashable] or array):
        None: uses df
        List[hashable]: uses df[y]
        array: uses pd.DataFrame(y, columns=[""])
    figure (bool or go.Figure):
        False: returns list of objects
        True: add objs to new figure and returns figure
        go.Figure: adds objs and returns figure
    go_class (str): Default class to use getattr(plotly.graph_objects, type)
    **kws: |
        Defaults to use with go_class(**kws).
        Special note: this can be customized per column uses. Example if
        y = ["a", "b"] you could specify a custom kws
        `line_color={"a": "red", "b": "blue"}` OR `line_color=["red", "blue"]`
        to customize per. Can also just specify one for all: `line_color="red"`

    Returns
    -------
    List[go.BaseTraceType]: Returns all the graph objects
    or
    go.Figure: If figure is True or go.Figure it'll return that figure with
        the graph objects on it.
    """
    x_data = _get_x_from_dataframe(df, x=x)
    y_data = _get_y_from_dataframe(df, y=y)
    df_kws = _get_kws_from_dataframe(y_data.keys(), go_class=go_class, **kws)

    objs = []
    for column in y_data:
        kwargs = df_kws.loc[column].dropna().to_dict()
        obj_class_name = kwargs.pop("go_class")
        obj_class = getattr(go, obj_class_name)
        objs.append(
            _get_plot_obj(x_data, y_data, column, obj_class=obj_class, **kwargs)
        )

    return figure_with_traces(objs, figure=figure)
