""" Unit tests for graph module
"""
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,no-self-use

import unittest

from data_science_tools import graph


EXAMPLE_GRAPH_A = {
    "A": ["C", "B"],
    "B": ["D"],
    "C": ["B", "D"],
}

EXAMPLE_GRAPH_B_CYCLE = {
    "A": ["C", "B"],
    "B": ["D"],
    "C": ["B", "D", "A"],
}


class TestSearchGraph(unittest.TestCase):
    def _assert_list_equal(self, list_actual, list_expected):
        self.assertEqual(len(list_actual), len(list_expected))
        lines = ["Lists do not match"]
        all_match = True
        for i, a in enumerate(list_actual):
            e = list_expected[i]
            if a == e:
                lines.append(f"{i}: {a} match")
            else:
                all_match = False
                lines.append(f"{i}: {a} != {e}")
        self.assertTrue(all_match, "\n".join(lines))

    def test_search_graph_depth_first(self):
        actual = []
        graph.search_graph(
            "A",
            get_children=EXAMPLE_GRAPH_A.get,
            callback=actual.append,
            depth_first=True,
        )
        expected = [
            ["A"],
            ["A", "B"],
            ["A", "B", "D"],
            ["A", "C"],
            ["A", "C", "D"],
            ["A", "C", "B"],
            ["A", "C", "B", "D"],
        ]
        self._assert_list_equal(actual, expected)

    def test_search_graph_breadth_first(self):
        actual = []
        graph.search_graph(
            "A",
            get_children=EXAMPLE_GRAPH_A.get,
            callback=actual.append,
            depth_first=False,
        )
        expected = [
            ["A"],
            ["A", "C"],
            ["A", "B"],
            ["A", "C", "B"],
            ["A", "C", "D"],
            ["A", "B", "D"],
            ["A", "C", "B", "D"],
        ]
        self._assert_list_equal(actual, expected)

    def test_search_graph_breadth_first_shortest_path(self):
        actual = []

        def found_shortest(path):
            nonlocal actual
            actual.append(path)
            return path[-1] == "D"

        graph.search_graph(
            "A",
            get_children=EXAMPLE_GRAPH_A.get,
            callback=found_shortest,
            depth_first=False,
        )
        expected = [
            ["A"],
            ["A", "C"],
            ["A", "B"],
            ["A", "C", "B"],
            ["A", "C", "D"],
        ]
        self._assert_list_equal(actual, expected)

    def test_search_graph_find_no_children_path(self):
        actual = []
        graph.search_graph(
            "A",
            get_children=EXAMPLE_GRAPH_A.get,
            callback_no_children=actual.append,
        )
        expected = [
            ["A", "B", "D"],
            ["A", "C", "D"],
            ["A", "C", "B", "D"],
        ]
        self._assert_list_equal(actual, expected)

    def test_search_graph_cycle_raise_error(self):
        try:
            graph.search_graph(
                "A",
                get_children=EXAMPLE_GRAPH_B_CYCLE.get,
            )
        except graph.SearchGraphCycleError:
            pass

    def test_search_graph_cycle_no_error(self):
        actual = []
        graph.search_graph(
            "A",
            get_children=EXAMPLE_GRAPH_B_CYCLE.get,
            callback=actual.append,
            raise_cycle_error=False,
        )
        expected = [
            ["A"],
            ["A", "B"],
            ["A", "B", "D"],
            ["A", "C"],
            ["A", "C", "D"],
            ["A", "C", "B"],
            ["A", "C", "B", "D"],
        ]
        self._assert_list_equal(actual, expected)

    def test_search_graph_callback_cycle(self):
        actual = []

        graph.search_graph(
            "A",
            get_children=EXAMPLE_GRAPH_B_CYCLE.get,
            callback=actual.append,
            callback_cycle_check=graph.cycle_check_child_in_path_n(2),
            raise_cycle_error=False,
        )
        expected = [
            ["A"],
            ["A", "B"],
            ["A", "B", "D"],
            ["A", "C"],
            ["A", "C", "A"],
            ["A", "C", "A", "B"],
            ["A", "C", "A", "B", "D"],
            ["A", "C", "A", "C"],
            # cycle ["A", "C", "A", "C", "A"],
            ["A", "C", "A", "C", "D"],
            ["A", "C", "A", "C", "B"],
            ["A", "C", "A", "C", "B", "D"],
            ["A", "C", "D"],
            ["A", "C", "B"],
            ["A", "C", "B", "D"],
        ]
        self._assert_list_equal(actual, expected)
