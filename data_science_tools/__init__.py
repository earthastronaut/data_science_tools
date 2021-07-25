""" Data Science Tools
"""
# flake8: noqa: F403,F401
# pylint: disable=import-outside-toplevel,global-statement


def get_version():
    """Get version number"""
    import os  # pylint: disable=redefined-outer-name

    with open(os.path.join(os.path.dirname(__file__), "__version__")) as buffer:
        return buffer.readline().strip()


__version__ = get_version()
__all__ = ["__version__"]


def import_all_modules():
    """Load all modules"""
    global __all__

    from . import (
        dataframe,
        graph,
        python_interactive,
        quantize,
        statistics,
        utils,
        weighted,
        matplotlib_tools,
        plotly_tools,
    )

    globals().update(locals())

    modules = [
        dataframe,
        graph,
        python_interactive,
        quantize,
        statistics,
        utils,
        weighted,
        matplotlib_tools,
        plotly_tools,
    ]

    for mod in modules:
        all_public = getattr(mod, "__all__", [])
        __all__ += all_public
        globals().update({name: getattr(mod, name) for name in all_public})
