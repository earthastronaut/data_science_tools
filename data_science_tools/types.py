""" For all common types. DO NOT IMPORT OTHER PACKAGE MODULES INTO THIS ONE
"""
# pylint: disable=missing-function-docstring

from typing import (
    Any,
    Callable,
    Dict,
    Deque,
    List,
    Sequence,
    Hashable,
    Iterable,
    Union,
    TypeVar,
)
from types import ModuleType

__all__ = [
    "Any",
    "Callable",
    "Dict",
    "Deque",
    "List",
    "Sequence",
    "Hashable",
    "Iterable",
    "ModuleType",
    "Union",
    "Node",
]

Node = TypeVar("Node", Hashable, str, int, float)
