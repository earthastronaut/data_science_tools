# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=reimported
# pylint: disable=missing-class-docstring
# pylitn: disable=no-self-use

# standard
import unittest

# external
import numpy as np
import pandas as pd

# relative
from .._plotters import (
    plot_scatter_filled,
    plot_dataframe,
)


class TestPlotScatterFilled(unittest.TestCase):
    def test_full(self):
        x = np.arange(10)
        fig = plot_scatter_filled(
            x,
            y=np.sin(x),
            upper_y=np.sin(x) + np.cos(x),
            lower_y=np.sin(x) - np.cos(x),
            line_color="rgb(255,0,0)",
            fill_opacity=0.2,
        )
        data = fig.to_dict()["data"]
        self.assertTrue(len(data), 3)
        self.assertIsNone(data[1].get("fillcolor"))
        self.assertEqual(data[2]["fillcolor"], "rgba(255,0,0,0.2)")

    def test_line_none(self):
        self.assertRaises(
            TypeError,
            plot_scatter_filled,
        )

    def test_line(self):
        x = np.arange(10)
        fig = plot_scatter_filled(
            x,
            y=np.sin(x),
        )
        data = fig.to_dict()["data"]
        self.assertTrue(len(data), 1)
        self.assertEqual(data[0]["type"], "scatter")

    def test_line_upper_only(self):
        x = np.arange(10)
        fig = plot_scatter_filled(
            x,
            y=np.sin(x),
            upper_y=np.sin(x) + np.cos(x),
            line_color="rgb(255,0,0)",
            fill_opacity=0.2,
        )
        data = fig.to_dict()["data"]
        self.assertTrue(len(data), 2)
        self.assertEqual(data[1]["fillcolor"], "rgba(255,0,0,0.2)")

    def test_line_lower_only(self):
        x = np.arange(10)
        fig = plot_scatter_filled(
            x,
            y=np.sin(x),
            lower_y=np.sin(x) - np.cos(x),
            line_color="rgb(255,0,0)",
            fill_opacity=0.2,
        )
        data = fig.to_dict()["data"]
        self.assertTrue(len(data), 2)
        self.assertEqual(data[1]["fillcolor"], "rgba(255,0,0,0.2)")

    def test_dataframe(self):
        x = np.arange(10)
        y = np.sin(x)
        df = pd.DataFrame(
            {
                "x": x,
                "middle": y,
                "above": y + 2,
                "below": y - 2,
            }
        )
        traces = plot_scatter_filled(
            df=df,
            x="x",
            y="middle",
            lower_y="below",
            upper_y="above",
            relative=False,
            figure=False,
        )
        self.assertTrue(len(traces), 3)
        actual = traces[0]
        np.testing.assert_array_equal(actual.x, df["x"].values)
        np.testing.assert_array_equal(actual.y, df["middle"].values)

        actual = traces[1]
        np.testing.assert_array_equal(actual.x, df["x"].values)
        np.testing.assert_array_equal(actual.y, df["above"].values)

        actual = traces[2]
        np.testing.assert_array_equal(actual.x, df["x"].values)
        np.testing.assert_array_equal(actual.y, df["below"].values)


class TestDataFramePlotter(unittest.TestCase):
    def test_plot_dataframe(self):
        df = pd.DataFrame(
            {
                "col1": np.arange(10),
                "col2": np.ones(10),
            }
        )
        fig = plot_dataframe(df)
        self.assertEqual(len(fig.data), 2)

        actual = [obj.name for obj in fig.data]
        expected = list(df)
        self.assertEqual(actual, expected)

    def test_plot_dataframe_select(self):
        df = pd.DataFrame(
            {
                "col1": np.arange(10),
                "col2": np.ones(10),
                "c3": np.zeros(10),
            }
        )
        traces = plot_dataframe(df, x=np.arange(10, 20), y=["col1", "c3"], figure=False)
        self.assertEqual(len(traces), 2)

        actual = [obj.name for obj in traces]
        expected = ["col1", "c3"]
        self.assertEqual(actual, expected)

    def test_plot_dataframe_parameters(self):
        df = pd.DataFrame(
            {
                "col1": np.arange(10),
                "col2": np.ones(10),
            }
        )
        traces = plot_dataframe(
            df,
            opacity=0.5,
            df_kws=dict(
                col1={
                    "line_color": "red",
                },
                col2={
                    "go_class": "Bar",
                    "marker": {
                        "color": "blue",
                    },
                },
            ),
            figure=False,
        )
        col1, col2 = traces
        self.assertEqual(col1.opacity, 0.5)
        self.assertEqual(col2.opacity, 0.5)

        self.assertEqual(col1.name, "col1")
        self.assertEqual(col2.name, "col2")

        self.assertEqual(col1.type, "scatter")
        self.assertEqual(col2.type, "bar")

        self.assertEqual(col1.line.color, "red")
        self.assertEqual(col2.marker.color, "blue")

    def test_plot_dataframe_parameters_df_kws(self):
        df = pd.DataFrame(
            {
                "col1": np.arange(10),
                "col2": np.ones(10),
            }
        )

        traces = plot_dataframe(
            df,
            opacity=0.5,
            df_kws=pd.DataFrame(
                {
                    "line_color": ["red", None],
                    "go_class": [None, "Bar"],
                    "marker_color": [None, "blue"],
                },
                index=["col1", "col2"],
            ),
            figure=False,
        )
        col1, col2 = traces
        self.assertEqual(col1.opacity, 0.5)
        self.assertEqual(col2.opacity, 0.5)

        self.assertEqual(col1.name, "col1")
        self.assertEqual(col2.name, "col2")

        self.assertEqual(col1.type, "scatter")
        self.assertEqual(col2.type, "bar")

        self.assertEqual(col1.line.color, "red")
        self.assertEqual(col2.marker.color, "blue")
