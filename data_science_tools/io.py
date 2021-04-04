""" Tools for reading and writing
"""
# standard
import abc
from collections import OrderedDict
import decimal
import datetime
import json
import logging
import io
import os
import importlib
import inspect
from types import ModuleType

# external
import numpy as np
import yaml

logger = logging.getLogger(__name__)


def get_object_import(obj, module=None, validate=True):
    """Create a path to the object import.

    e.g. glob would become "glob.glob"

    Parameters:
        obj (object, str):
                Name of the object or the object itself. Needs to have
                __name__ attribute which functions and classes have.
        module (None, str, ModuleType):
                Module to use for the object. If None then will inspect the object
                for the module. If string then uses that. If ModuleType then uses
                __name__ from module.

    Returns:
        str
    """
    module_name = None
    if isinstance(module, ModuleType):
        module_name = module.__name__
    elif isinstance(module, str):
        module_name = module

    object_name = None
    if isinstance(obj, str):
        object_name = obj
    elif not hasattr(obj, "__name__"):
        raise TypeError(f"Invalid type {type(obj)} must have __name__")
    else:
        object_name = obj.__name__
        if module_name is None:
            module_name = inspect.getmodule(obj).__name__

    if module_name is None:
        raise TypeError(f"No module name found for {module} and {obj}")
    if object_name is None:
        raise TypeError(f"No object name found for {obj}")
    if "." in object_name:
        raise TypeError(f"Object name should not have dots: {object_name}")

    object_path = module_name + "." + object_name
    if validate:
        import_object(object_path)
    return object_path


def import_object(object_path, namespace=None):
    """Resolve object path into an object

    e.g. "glob.glob" would return "glob" function

    Parameters:
        object_path (str): Path to the object or object. "module.object_name"
        namespace (None, str, or module): Any namespace object.
            * If None then assume from object_path or builtins.
            * If str then import as module
            * Else use getattr(namespace, object_name)

    Returns:
        Any

    """
    if isinstance(object_path, str):
        module_name, _, obj_name = object_path.rpartition(".")
        if module_name == "":
            if namespace is None:
                namespace = importlib.import_module("builtins")
            elif isinstance(namespace, str):
                namespace = importlib.import_module(namespace)
        else:
            namespace = importlib.import_module(module_name)
        obj = getattr(namespace, obj_name)
        return obj
    else:
        return object_path


def get_name(function_or_object):
    """Resolve the name of the cost function"""
    if hasattr(function_or_object, "name"):
        # object can provide a name
        return function_or_object.name
    elif hasattr(function_or_object, "__name__"):
        # functions have __name__
        return function_or_object.__name__
    else:
        # class can act as a name
        return function_or_object.__class__.__name__.lower()
