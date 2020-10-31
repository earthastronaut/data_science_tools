""" Graph based tools
"""
from collections import deque
import logging

from .types import (
    CallableHashableArg,
    CallableListHashableArg,
    Hashable,
)

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


class SearchGraphCycleError(Exception):
    """Raise this error when a cycle is found when searching a graph"""


def search_graph(
    start: Hashable,
    get_children: CallableHashableArg,
    callback: CallableListHashableArg = None,
    callback_no_children: CallableListHashableArg = None,
    depth_first: bool = True,
    raise_cycle_error: bool = True,
):
    """Graph search function avoiding cicular patterns.
    Parameters
        start: Node (aka key) in the graph (aka dict)
        get_children: Returns children nodes in the graph. If graph is
            a dictionary of node keys and list of children. Then provide
            `get_children=graph.get`.
        callback: If provided, calls `callback(path)` for
            each path in the graph. If this returns True then
            the goal was achieved and it stops searching.
        callback_no_children: If provided, calls `callback_no_children(path)` when
            finds an end node with no children. Note: if your get_children is a
            generator this will not work.
        depth_first: If True then does a depth first search
            otherwise it's dreath first
        raise_cycle_error: If True then raise an error if cycle is found otherwise
            silently ignore the cycle and move on.

    Returns
        None or List[Hashable]: Returns None or the current path when
            `callable(path) == True`.
    """
    stack = deque()
    stack.append((start, [start], {start}))
    pop_node = stack.pop if depth_first else stack.popleft

    while len(stack) > 0:
        node, path, path_lookup = pop_node()

        # logger.debug(f"Path: {path}")
        if callback is not None:
            if callback(path):
                return path

        children = get_children(node)
        if not children:
            if callback_no_children:
                callback_no_children(path)
            continue

        for child in children:
            if child in path_lookup:
                if raise_cycle_error:
                    raise SearchGraphCycleError(path + [child])
                continue
            stack.append((child, path + [child], path_lookup.union({child})))
