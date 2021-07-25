""" Technically not data science tools but really useful tools
when working interactively with python on the command line.

Documented in this gist
https://gist.github.com/earthastronaut/2c4b7fe6c8c8c62c5eeb2430ba6f7888


"""
# pylint: disable=line-too-long,import-outside-toplevel
# pylint: disable=exec-used,redefined-builtin,invalid-name


# MIT License
# Copyright 2018 Dylan Gregersen
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files(the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and / or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import importlib
import logging
import warnings
from typing import Dict, Sequence
from types import ModuleType

try:
    import builtins
except ImportError:
    import __builtin__ as builtins  # type: ignore

from .graph import search_graph

__all__ = [
    "execfile",
    "reload",
    "dirquery",
    "fprint",
]

logger = logging.getLogger(__name__)
PY3 = sys.version[0] == "3"


def interactive_only_warning():
    """Raise a warning that tools are only suppose to be interactive"""
    msg = "This tool is only meant to be used interactivcely and not in a script"
    warnings.warn(msg)


if PY3:
    simple_reload = importlib.reload

    # bring back execfile and reload for interactive use
    def execfile(filepath, globals_=None, locals_=None):
        """Implementation of python-2 execfile

        This function was deprecated in Python 3 in favor of using exec(). In
        interactive development of scripts I still find it a helpful function
        to re-execute all the code.
        """
        interactive_only_warning()
        globals_ = globals_ or globals()
        locals_ = locals_ or locals()
        with open(filepath, "r") as fptr:
            # import runpy
            # result = runpy.run_path(f,globals,locals)
            # globals.update(result) ??
            try:
                source = fptr.read() + "\n"
                abs_filepath = os.path.abspath(filepath)
                code = compile(source, abs_filepath, "exec")
                exec(code, globals_, locals_)  # nosec
            except KeyboardInterrupt:
                return


else:
    execfile = builtins.execfile
    simple_reload = builtins.reload


def dirquery(obj, pattern=None, case_sensitive=False, flags=None):
    """Take dir of an obj and search for matches based on pattern.

    Parameters
        pattern (string): Regular expression to search with.
        obj (object): Any python object or namespace.
        case_sensitive (bool): Should search be case sensitive.
        flags: passed to re.search(pattern, attribute, **kws)

    Returns
        List(str): List of all matching attribute names.

    """
    import re

    interactive_only_warning()

    if pattern is None:
        return dir(obj)

    flags = flags or (re.IGNORECASE if case_sensitive else 0)

    return [
        attribute
        for attribute in dir(obj)
        if re.search(pattern, attribute, flags=flags) is not None
    ]


FPRINT_TEMPLATE = """
# #########################################
# filepath: {filepath}
# start_line: {start_line}
# end_line: {end_line}
# #########################################

{code_text}
"""


def fprint(func, max_line_count=100, exclude_docstring=True, show=True):
    """Prints out the source code (from file) for a function
    inspect.getsourcelines(func)

    Parameters
        func (function): Any python function. Does not work on non-native python
            functions like many builtins.
        max_line_count (int): Maximum number of code lines to return. None will
            include all lines.
        exclude_docstring (bool): Doc string can be accessed with help(func)
        show (bool): If true print function code else return code lines.

    Returns
        None OR List[str]: None if show is true else returns list of code lines.

    """
    import inspect

    interactive_only_warning()

    # Optional pagination using ipython if found
    # python2-3 capatible
    ModuleNotFound = getattr(builtins, "ModuleNotFoundError", builtins.ImportError)
    try:
        from IPython.core.page import page as pager
    except (ImportError, ModuleNotFound):
        pager = None

    filepath = inspect.getsourcefile(func)
    code_lines, start_line = inspect.getsourcelines(func)
    end_line = start_line + len(code_lines)

    doc_line_count = func.__doc__.count("\n") if func.__doc__ is not None else 0
    if exclude_docstring and doc_line_count > 0:
        msg = '    """ <for docstring run help({name})> """\n'.format(
            name=func.__name__
        )
        doc_line_i = 1 + doc_line_count + 1
        code_lines = code_lines[:1] + [msg] + code_lines[doc_line_i:]

    if show:
        template_kws = {
            "filepath": filepath,
            "start_line": start_line,
            "end_line": end_line,
        }

        if pager:
            template_kws["code_text"] = "".join(code_lines)
            pager(FPRINT_TEMPLATE.format(**template_kws))
        else:
            template_kws["code_text"] = "".join(code_lines[:max_line_count])
            print(FPRINT_TEMPLATE.format(**template_kws))
        return None
    else:
        return code_lines[:max_line_count]


def generate_package_dependency_graph(package: ModuleType):
    """Search a package and find all it's children dependencies.

    Args:
        package (ModuleType): Any module.

    Returns:
        Dict: Keys are each module and the values are an
            interable of the children submodules.
    """
    dependency_graph = {}
    package_name = package.__name__

    def get_submodules(module_name: str) -> Sequence[str]:
        """Search a module and find it's children submodules related to the
        parent package"""
        nonlocal dependency_graph, package_name

        if module_name not in dependency_graph:
            module = importlib.import_module(module_name)
            # logger.info('Module: %s aka %s', module_name, module.__name__)
            submodules = []
            for obj_name in dir(module):
                obj = getattr(module, obj_name)
                if isinstance(obj, ModuleType):
                    submodule_name = obj.__name__
                elif hasattr(obj, "__module__"):
                    submodule_name = obj.__module__
                else:
                    continue
                # logger.info('Checking: %s', submodule_name)
                is_submodule_of_package = submodule_name.startswith(package_name)
                if is_submodule_of_package and module_name != submodule_name:
                    submodules.append(submodule_name)
            dependency_graph[module_name] = submodules
        return dependency_graph[module_name]

    search_graph(
        start=package.__name__,
        get_children=get_submodules,
        depth_first=True,
        raise_cycle_error=True,
    )

    logger.info("Dependency graph: %s", dependency_graph)
    return dependency_graph


def reload_from_dependency_graph(dependency_graph: Dict):
    """Reload from the graph of dependencies.

    Args:
        dependency_graph (Dict): Keys are each module and the values are an
            interable of the children submodules.
    """
    reload_graph = {
        module_name: set(submodules)
        for module_name, submodules in dependency_graph.items()
    }
    while len(reload_graph) > 0:
        keys = list(reload_graph.keys())
        reloaded_modules = []
        for module_name in keys:
            submodules_name = reload_graph[module_name]
            # if there are no children then import and remove from graph
            if len(submodules_name) == 0:
                logger.info("Reload %s", module_name)
                simple_reload(importlib.import_module(module_name))
                reloaded_modules.append(module_name)
                del reload_graph[module_name]

        # remove all imported from the children of other modules
        for module_name in reload_graph:
            for reloaded_module in reloaded_modules:
                if reloaded_module in reload_graph[module_name]:
                    reload_graph[module_name].remove(reloaded_module)


def reload(package: ModuleType, recursive: bool = True):
    """Reload a package

    Args:
        package (ModuleType): A module to import it and all children.
        recursive (bool): If True then looks at all children of the package
            and reloads them from the edge inward to all new updates are
            propogated to the top level.
    Returns:
        ModuleType: The reloaded package.

    """
    interactive_only_warning()
    if not recursive:
        return importlib.reload(package)

    dependency_graph = generate_package_dependency_graph(package)
    reload_from_dependency_graph(dependency_graph)
    return package
