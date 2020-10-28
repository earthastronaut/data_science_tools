""" For all common types. DO NOT IMPORT OTHER PACKAGE MODULES INTO THIS ONE
"""
from typing import Dict, List, Hashable, Iterable, Callable, Union, Any
from types import ModuleType

__all__ = [
    'Callable',
    'CallableHashableArg',
    'CallableListHashableArg',
    'Dict',
    'List',
    'Hashable',
    'Iterable',
    'ModuleType',
    'Union',
    'Any',
]


CallableHashableArg = Callable[[Hashable], Any]
CallableListHashableArg = Callable[[List[Hashable]], Any]
