""" Axis formatting functions.
"""
import matplotlib
import pylab as plt


__all__ = [
    "humanize_number",
    "axis_format_humanize_number",
    "axis_format_time",
    "axis_format_percent",
]


def humanize_number(x):
    """Convert number to human readable string."""
    abs_x = abs(x)
    if abs_x > 1e6:
        return f"{x/1e6:.0f}m"
    elif abs_x > 1e3:
        return f"{x/1e3:.0f}k"
    elif abs_x > 10:
        return f"{x:.0f}"
    else:
        return f"{x:.3f}"


def axis_format_percent(xaxis=False, fmt="{x:.0%}"):
    """Format axis ticks as percent"""
    if xaxis:
        axis = plt.gca().xaxis
    else:
        axis = plt.gca().yaxis
    axis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(fmt))


def axis_format_humanize_number(xaxis=False):
    """Format axis ticks as human number"""
    if xaxis:
        axis = plt.gca().xaxis
    else:
        axis = plt.gca().yaxis

    def fmtr(value, _):
        return humanize_number(value)

    axis.set_major_formatter(matplotlib.ticker.FuncFormatter(fmtr))


def axis_format_time(xaxis=True, month_locator_kws=None):
    """Format axis ticks as time"""
    if xaxis:
        axis = plt.gca().xaxis
    else:
        axis = plt.gca().yaxis

    month_locator_kws_defaults = {
        "bymonth": 3,
    }
    month_locator_kws_defaults.update(month_locator_kws or {})
    axis.set_major_formatter(
        plt.matplotlib.dates.AutoDateFormatter(
            plt.matplotlib.dates.MonthLocator(**month_locator_kws_defaults)
        )
    )
