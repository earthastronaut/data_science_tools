""" Graph based tools
"""
from collections import deque
import logging

from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    Sequence,
    Hashable,
    Union,
    TypeVar,
)

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Node = TypeVar("Node", Hashable, str, int, float)


class SearchGraphCycleError(Exception):
    """Raise this error when a cycle is found when searching a graph"""


def cycle_check_child_in_path_n(
    count: int,
) -> Callable[[Node, Sequence[Node], Dict[Node, int]], bool]:
    """Create a function which checks if the child has been in the path n times.

    Parameters
        count: number of times a child can appear in the path.

    Returns
        bool: if >= count
    """

    def cycle_check(
        child: Node,
        path: Sequence[Node],  # pylint: disable=unused-argument
        path_lookup: Dict[Node, int],
    ) -> bool:
        return path_lookup.get(child, -1) >= count

    return cycle_check


def cycle_check_child_in_path(
    child: Node,
    path: Sequence[Node],  # pylint: disable=unused-argument
    path_lookup: Dict[Node, int],
) -> bool:
    """Check if child node is in the path"""
    return child in path_lookup


def search_graph(
    start: Node,
    get_children: Callable[[Node], Sequence[Node]],
    callback: Callable[[Sequence[Node]], Union[bool, None]] = None,
    callback_no_children: Callable[[Sequence[Node]], Any] = None,
    callback_cycle_check: Callable[
        [Node, Sequence[Node], Dict[Node, int]], bool
    ] = cycle_check_child_in_path,
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
        callback_cycle_check: Will call with the child and the path and decide
            if there is a cycle in the graph. Provides a hash lookup of the number
            of times a child has been visited. By default if child is in this
            lookup then it returns true and raises error or stops depending on the
            raise_cycle_error.
        depth_first: If True then does a depth first search
            otherwise it's dreath first
        raise_cycle_error: If True then raise an error if cycle is found otherwise
            silently ignore the cycle and move on.

    Returns
        None or List[Hashable]: Returns None or the current path when
            `callable(path) == True`.
    """
    stack: Deque = deque()
    stack.append((start, [start], {start: 1}))
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
            if callback_cycle_check(child, path, path_lookup):
                if raise_cycle_error:
                    raise SearchGraphCycleError(path + [child])
                continue

            child_path_lookup = path_lookup.copy()
            child_path_lookup.setdefault(child, 0)
            child_path_lookup[child] += 1
            stack.append((child, path + [child], child_path_lookup))
