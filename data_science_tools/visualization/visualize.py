from datetime import datetime, timedelta

import matplotlib.pylab as plt
import numpy as np
import seaborn as sns

from data_science_tools.utils import DotDict

__all__ = [
    'plot_bars',
    'crayons',
    'Crayons',
    'pad_axis_limits',
]


class Crayons(DotDict):
    pass


crayons = Crayons({k.lower().replace(' ', '_'): v for k, v in sns.crayons.items()})
crayons.update({
    'alert_danger': crayons.brick_red,
    'alert_info': crayons.blue_green,
    'alert_warning': crayons.goldenrod,
})


def plot_bars(x, heights, width=None, align='center', y_base=0, ax=None, **rectangle_kws):
    """ Plot rectangular bars.

    Args:
        x (List): X points of the bars. Can handle dates.
        heights (List): Heights of the bars, can be negative.
        width (float or Any): Used with the center to determine the bar
            dimensions.
        align (str): Where to align the x.
            'center': x is the center.
            'left': x is the left edge.
            'right': x is the right edge.
        y_base (float): Base of the bars.
        ax (matplotlib.axes.Axes): Axis object, otherwise uses plt.gca().
        **rectangle_kws: passed to all plt.Rectangle(**rectangle_kws).

    Returns:
        List[plt.Rectangle]: List of the rectangle patches.

    """
    ax = ax or plt.gca()

    if not len(x):
        # don't plot anything because there isn't any
        return []

    # is x axis datetime objects?
    xpt0 = x[0]
    x_is_datetime = isinstance(xpt0, datetime)

    # get width of the bars
    if width is None:
        if len(x) > 1:
            xpt1 = x[1]
            diff = xpt1 - xpt0
            width = diff * 0.8
        else:
            if x_is_datetime:
                width = timedelta(days=1)
            else:
                width = 1
    elif isinstance(width, (float, int)) and x_is_datetime:
        width = timedelta(days=width)

    half_width = width / 2.0

    # get the x and y bounds
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    is_first = True
    rectangles = []
    for xpt, height in zip(x, heights):
        if height < 0:
            height = abs(height)
            rect_ymin = y_base - height
            rect_ymax = y_base
        else:
            rect_ymin = y_base
            rect_ymax = rect_ymin + height

        if align == 'center':
            rect_xmin = xpt - half_width
            rect_xmax = xpt + half_width
        elif align == 'left':
            rect_xmin = xpt
            rect_xmax = xpt + width
        elif align == 'right':
            rect_xmin = xpt - width
            rect_xmax = xpt
        else:
            raise ValueError(
                f'unknown value for where "{where}" not one of (center, right, left)'  # noqa
            )

        kws = {
            'alpha': 0.8,
        }
        kws.update(rectangle_kws)
        if not is_first:
            kws.pop('label', None)
        rect = plt.Rectangle(
            xy=(rect_xmin, rect_ymin),
            height=height,
            width=width,
            **kws,
        )
        ax.add_patch(rect)
        rectangles.append(rect)

        if isinstance(rect_xmin, datetime) and isinstance(xmin, float):
            if xmin == 0.0:
                xmin = rect_xmin
            else:
                xmin = plt.matplotlib.dates.num2date(xmin).replace(tzinfo=rect_xmin.tzinfo)  # noqa
        if isinstance(rect_xmax, datetime) and isinstance(xmax, float):
            if xmax == 1.0:
                xmax = rect_xmax
            else:
                xmax = plt.matplotlib.dates.num2date(xmax).replace(tzinfo=rect_xmax.tzinfo)  # noqa

        xmin = min(xmin, rect_xmin)
        xmax = max(xmax, rect_xmax)
        ymin = min(ymin, rect_ymin)
        ymax = max(ymax, rect_ymax)

        is_first = False

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    return rectangles


def pad_axis_limits(padding=0.05, yaxis=True, ax=None):
    """ Pad the axis limits by a percentage.

    Args:
        padding (float): Size of padding to add to min and max limit.
        yaxis (bool): Apply to the yaxis else apply to xaxis.
        ax (plt.Axes): Matplotlib plot axes. Uses plt.gca() if None.

    Returns:
        (float, float): The new boundary limits.

    """
    ax = ax or plt.gca()
    if yaxis:
        axis_method = 'ylim'
    else:
        axis_method = 'xlim'

    dmin, dmax = getattr(ax, f'get_{axis_method}')()
    if padding < 1.0:
        padding_size = abs((dmax - dmin) * padding)
    else:
        padding_size = abs(padding)

    new_min = dmin - padding_size
    new_max = dmax + padding_size
    getattr(ax, f'set_{axis_method}')(new_min, new_max)
    return new_min, new_max
