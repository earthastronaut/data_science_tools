# pylint: disable=missing-module-docstring,missing-function-docstring
# pylint: disable=reimported,missing-class-docstring,no-self-use

# standard
import unittest

# external
import numpy as np

# relative
from .. import _subplots as subplots


class TestSubplots(unittest.TestCase):
    def test_figure_subplot_masking(self):
        ax = subplots.FigureSubplot(row=2, col=2, secondary_y=False)
        ax.add_scatter(
            x=[1, 2, 3],
            y=[3, 2, 1],
        )
        ax.update_layout(
            # title="hello",
            yaxis4_title="foo",
            xaxis4_title="bar",
            xaxis4_range=[0, 10],
        )
        data = ax.to_dict()["data"]
        expected = [
            {
                "x": [1, 2, 3],
                "y": [3, 2, 1],
                "type": "scatter",
                "xaxis": "x4",
                "yaxis": "y4",
            }
        ]
        self.assertEqual(data, expected)
        layout = ax.to_dict()["layout"]
        expected_keys = {
            "xaxis",
            "yaxis",
            "xaxis2",
            "yaxis2",
            "xaxis3",
            "yaxis3",
            "xaxis4",
            "yaxis4",
        }
        missing = expected_keys - set(layout)
        self.assertFalse(len(missing), str(missing))

        expected = {
            "anchor": "y4",
            "domain": [0.55, 1.0],
            "title": {"text": "bar"},
            "range": [0, 10],
        }
        self.assertEqual(layout["xaxis4"], expected)

        expected = {"anchor": "x4", "domain": [0.0, 0.425], "title": {"text": "foo"}}
        self.assertEqual(layout["yaxis4"], expected)

    def test_make_subplots_shapes(self):
        axes = subplots.create_subplots(2, 2)
        self.assertIsInstance(axes, np.ndarray)
        self.assertEqual(axes.ndim, 3)
        self.assertEqual(axes.shape, (2, 2, 1))
        self.assertIsInstance(axes[0, 0, 0], subplots.FigureSubplot)

        axes = subplots.create_subplots(2, 2, secondary_y=True)
        self.assertIsInstance(axes, np.ndarray)
        self.assertEqual(axes.ndim, 3)
        self.assertEqual(axes.shape, (2, 2, 2))

        axes = subplots.create_subplots(rows=2, subplot_count=8, secondary_y=True)
        self.assertIsInstance(axes, np.ndarray)
        self.assertEqual(axes.ndim, 3)
        self.assertEqual(axes.shape, (2, 4, 2))
