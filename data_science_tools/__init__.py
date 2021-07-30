""" Data Science Tools
"""
# flake8: noqa: F403,F401
# pylint: disable=import-outside-toplevel,global-statement


def get_version() -> str:
    """Get version number"""
    import os  # pylint: disable=redefined-outer-name

    filepath = os.path.join(os.path.dirname(__file__), "__version__")
    if os.path.exists(filepath):
        with open(filepath) as buffer:
            return buffer.readline().strip()
    else:
        return "dev"


__version__ = get_version()
__all__ = ["__version__"]


def import_tools(names=None) -> None:
    """Load tools into the main namespace

    Purpose
    -------
    This is to make it easier to use the various tools within this package.
    Instead of tools.plotly_tools.subplots.make_subplots it imports to tools.make_subplots.

    Also allows to opt-in for importing modules which may not be necessary. By default
    none are loaded so if someone wanted something specific they can import just that
    and nothing else. e.g. `from data_science_tools import graph`.

    Parameters
    ----------
    names: List[str] - Names of modules/tool sets to load. By default loads all.
    """
    global __all__
    import importlib

    names = names or [
        "dataframe",
        "graph",
        "python_interactive",
        "quantize",
        "statistics",
        "utils",
        "weighted",
        "matplotlib_tools",
        "plotly_tools",
    ]

    for module_name in names:
        module = importlib.import_module(f"{__package__}.{module_name}")
        names = module.__all__  # type: ignore
        namespace = {name: getattr(module, name) for name in names}  # type: ignore
        namespace[module_name] = module  # type: ignore
        __all__ += namespace.keys()  # type: ignore
        globals().update(namespace)  # type: ignore
