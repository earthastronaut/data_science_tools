""" Technically not data science tools but really useful tools
when working interactively with python on the command line.

Documented in this gist https://gist.github.com/earthastronaut/2c4b7fe6c8c8c62c5eeb2430ba6f7888


"""
# pylint: disable=line-too-long,import-outside-toplevel,exec-used,redefined-builtin,invalid-name

# %%

# MIT License
# Copyright 2018 Dylan Gregersen
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import importlib

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

__all__ = [
    'execfile',
    'reload',
    'dirquery',
    'fprint',
]

PY3 = sys.version[0] == "3"

if PY3:
    reload = importlib.reload

    # bring back execfile and reload for interactive use
    def execfile(filepath,  globals_=None, locals_=None):
        """ Implementation of python-2 execfile

        This function was deprecated in Python 3 in favor of using exec(). In
        interactive development of scripts I still find it a helpful function
        to re-execute all the code.
        """
        globals_ = globals_ or globals()
        locals_ = locals_ or locals()
        with open(filepath, "r") as fptr:
            # import runpy
            # result = runpy.run_path(f,globals,locals)
            # globals.update(result) ??
            try:
                source = fptr.read() + "\n"
                abs_filepath = os.path.abspath(filepath)
                code = compile(source, abs_filepath, 'exec')
                exec(code, globals_, locals_)
            except KeyboardInterrupt:
                return
else:
    execfile = builtins.execfile
    reload = builtins.reload


def dirquery(obj, pattern=None, case_sensitive=False, flags=None):
    """ Take dir of an obj and search for matches based on pattern.

    Parameters
        pattern (string): Regular expression to search with.
        obj (object): Any python object or namespace.
        case_sensitive (bool): Should search be case sensitive.
        flags: passed to re.search(pattern, attribute, **kws)

    Returns
        List(str): List of all matching attribute names.

    """
    import re

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
    """ Prints out the source code (from file) for a function
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

    # Optional pagination using ipython if found
    # python2-3 capatible
    ModuleNotFound = getattr(
        builtins, 'ModuleNotFoundError', builtins.ImportError
    )
    try:
        from IPython.core.page import page as pager
    except (ImportError, ModuleNotFound):
        pager = None

    filepath = inspect.getsourcefile(func)
    code_lines, start_line = inspect.getsourcelines(func)
    end_line = start_line + len(code_lines)

    doc_line_count = func.__doc__.count('\n') if func.__doc__ is not None else 0
    if exclude_docstring and doc_line_count > 0:
        msg = '    """ <for docstring run help({name})> """\n'.format(
            name=func.__name__
        )
        code_lines = (
            code_lines[:1]
            + [msg]
            + code_lines[1 + doc_line_count + 1:]
        )

    if show:
        template_kws = {
            'filepath': filepath,
            'start_line': start_line,
            'end_line': end_line,
        }

        if pager:
            template_kws['code_text'] = ''.join(code_lines)
            pager(FPRINT_TEMPLATE.format(**template_kws))
        else:
            template_kws['code_text'] = ''.join(code_lines[:max_line_count])
            print(FPRINT_TEMPLATE.format(**template_kws))
        return None
    else:
        return code_lines[:max_line_count]
