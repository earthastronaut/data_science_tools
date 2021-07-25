""" Data Science Tools
"""
# flake8: noqa: F403,F401
# pylint: disable=import-outside-toplevel,global-statement


def get_version() -> str:
    """Get version number"""
    import os  # pylint: disable=redefined-outer-name

    with open(os.path.join(os.path.dirname(__file__), "__version__")) as buffer:
        return buffer.readline().strip()


__version__ = get_version()
__all__ = ["__version__"]


def import_all_modules() -> None:
    """Load all modules"""
    global __all__
    import importlib

    modules = [
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

    for module_name in modules:
        module = importlib.import_module(f"{__package__}.{module_name}")
        names = module.__all__  # type: ignore
        namespace = {name: getattr(module, name) for name in names}  # type: ignore
        namespace[module_name] = module  # type: ignore
        __all__ += namespace.keys()  # type: ignore
        globals().update(namespace)  # type: ignore
