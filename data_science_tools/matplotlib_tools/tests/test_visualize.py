""" Unit tests for graph module
"""
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,no-self-use

import unittest

import matplotlib.pylab as plt

from .. import visualize


class TestVisualize(unittest.TestCase):
    def setUp(self):
        plt.cla()
        plt.clf()

    def _assert_dict_equal(self, dict_actual, dict_expected, ignore_keys=None):
        self.assertEqual(type(dict_actual), type(dict_expected))
        self.assertEqual(set(dict_actual.keys()), set(dict_expected.keys()))
        ignore_keys = ignore_keys or set()
        lines = ["Dict actual != expected"]
        for key_a, value_a in dict_actual.items():
            if key_a in ignore_keys:
                continue
            value_e = dict_expected[key_a]
            if value_a == value_e:
                lines.append(f"{key_a}: match")
            else:
                lines.append(f"{key_a}: {value_a} != {value_e}")
                not_true = False
                self.assertTrue(not_true, "\n".join(lines))

    def test_color_palette(self):
        expected = ["#443983", "#31688e", "#21918c", "#35b779", "#90d743"]
        actual = list(visualize.color_palette(len(expected)))
        self.assertEqual(actual, expected)

    def _assert_matplotlib_rectangles_list(
        self, rectanges_actual, rectangles_expected, **kws
    ):
        kws.setdefault(
            "ignore_keys",
            {
                "_axes",
                "figure",
                "_transform",
                "_transformSet",
                "clipbox",
                "_remove_method",
                "_rect_transform",
            },
        )
        self.assertEqual(len(rectanges_actual), len(rectangles_expected))
        for i, actual in enumerate(rectangles_expected):
            expected = rectangles_expected[i]
            self._assert_dict_equal(
                actual.__getstate__(), expected.__getstate__(), **kws
            )

    def test_plot_bars(self):
        actual = visualize.plot_bars(x=[1, 2], heights=[1, 2], label="yo", hatch="/")

        expected = [
            plt.Rectangle(
                # if align == "center":
                #     rect_xmin = xpt - half_width
                #     rect_xmax = xpt + half_width
                xy=(
                    0.6,
                    0,
                ),
                height=1,
                width=0.8,  # width = diff * 0.8
                alpha=0.8,
                label="yo",
                hatch="/",
            ),
            plt.Rectangle(
                # if align == "center":
                #     rect_xmin = xpt - half_width
                #     rect_xmax = xpt + half_width
                xy=(
                    1.6,
                    0,
                ),
                height=2,
                width=0.8,  # width = diff * 0.8
                alpha=0.8,
                hatch="/",
            ),
        ]
        self._assert_matplotlib_rectangles_list(actual, expected)

    def test_plot_bars_align_left(self):
        actual = visualize.plot_bars(x=[1, 2], heights=[1, 2], label="yo", hatch="/")

        expected = [
            plt.Rectangle(
                # if align == "center":
                #     rect_xmin = xpt - half_width
                #     rect_xmax = xpt + half_width
                xy=(
                    1,
                    0,
                ),
                height=1,
                width=0.8,  # width = diff * 0.8
                alpha=0.8,
                label="yo",
                hatch="/",
            ),
            plt.Rectangle(
                # if align == "center":
                #     rect_xmin = xpt - half_width
                #     rect_xmax = xpt + half_width
                xy=(
                    2,
                    0,
                ),
                height=2,
                width=0.8,  # width = diff * 0.8
                alpha=0.8,
                hatch="/",
            ),
        ]

        self._assert_matplotlib_rectangles_list(actual, expected)

    def test_plot_bars_align_right(self):
        actual = visualize.plot_bars(
            x=[1, 2], heights=[1, 2], width=1, label="yo", hatch="/"
        )

        expected = [
            plt.Rectangle(
                xy=(
                    2,
                    0,
                ),
                height=1,
                width=1,
                alpha=0.8,
                label="yo",
                hatch="/",
            ),
            plt.Rectangle(
                xy=(
                    3,
                    0,
                ),
                height=2,
                width=1,
                alpha=0.8,
                hatch="/",
            ),
        ]

        self._assert_matplotlib_rectangles_list(actual, expected)

    def test_axis_limits_y(self):
        ax = plt.gca()
        actual = visualize.pad_axis_limits(ax=ax)
        expected = (-0.05, 1.05)
        self.assertEqual(actual, expected)
        self.assertEqual(ax.get_ylim(), expected)
        self.assertEqual(ax.get_xlim(), (0, 1))

    def test_axis_limits_x(self):
        ax = plt.gca()
        actual = visualize.pad_axis_limits(yaxis=False, ax=ax)
        expected = (-0.05, 1.05)
        self.assertEqual(actual, expected)
        self.assertEqual(ax.get_xlim(), expected)
        self.assertEqual(ax.get_ylim(), (0, 1))
