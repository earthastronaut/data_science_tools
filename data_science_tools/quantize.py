""" Quantize values to nearby points.
"""
import unittest

import numpy as np
import pandas as pd  # optional for quantize_hist

__all__ = [
    "quantize_values",
    "quantize_hist",
]


def get_quantize_centers(values, centers=None):
    """Get the default centers as array given some values"""
    if centers is None:
        centers = np.linspace(np.min(values), np.max(values), 10)
    elif isinstance(centers, int):
        centers = np.linspace(np.min(values), np.max(values), centers)
    return np.asarray(centers)


def quantize_values(values, centers=None):
    """On a particular 1d latice, quantize points to nearest

    Args:
        values (ndarray[Float]): Array of values to quantize to the centers
        centers (ndarray[Float]): Center values to quantize to. If None it will
            attempt to get the centers from the values.

    Returns:
        one of:
            np.ndarray:
                If isinstance(value, np.ndarray)
                Array same as values but quantized to the centers. If values is
                ndarray. shape == values.shape
            pd.Series:
                If isinstance(value, pd.Series)
                Series same as values but quantized to centers. If values is
                pd.Series. index == values.index
    """
    nanmask = np.isnan(values)
    centers = get_quantize_centers(values, centers)
    midpoints = (centers[1:] + centers[:-1]) * 0.5
    idx = np.digitize(values, midpoints)
    quant = centers[idx]
    if np.any(nanmask):
        try:
            quant[nanmask] = np.nan
        except ValueError:
            quant = quant.astype(float)
            quant[nanmask] = np.nan

    if isinstance(values, pd.Series):
        return pd.Series(quant, index=values.index)
    else:
        return quant


def quantize_hist(values, centers=None):
    """Quantize values to 1d lattice near center points and aggregate count.

    Args:
        values (ndarray[Float]): Array of values to quantize to the centers
        centers (ndarray[Float]): Center values to quantize to.

    Returns:
        (pandas.Series): Index is the centers and values are count of values
            which quantized to that center.
    """
    centers = get_quantize_centers(values, centers)
    quantized_values = quantize_values(values, centers=centers)
    return pd.Series(quantized_values).value_counts().reindex(centers).fillna(0)


class QuantizeTest(unittest.TestCase):
    """Unittests for quantize functions"""

    def test_quantize_values(self):
        """test"""
        quantize = np.array([-5, 2, 10])
        values = np.array([-10, -4, 1, 1, 1, 20, 5, 5.9, 7, 7, 16, 17])
        solution = np.array([-5, -5, 2, 2, 2, 10, 2, 2, 10, 10, 10, 10])
        self.assertTrue(np.all(quantize_values(values, quantize) == solution))

    @staticmethod
    def test_quantize_hist():
        """test"""
        quantize = np.array([-5, 2, 10])
        values = np.array([-10, -4, 1, 1, 1, 20, 5, 5.9, 7, 7, 16, 17])
        actual = quantize_hist(values, quantize)
        expected = pd.Series([2, 5, 5], index=[-5, 2, 10])
        pd.testing.assert_series_equal(actual, expected)

    @staticmethod
    def test_quantize_nulls():
        """test"""
        values = np.array([2, 2, np.nan, 5, 2, np.nan, 4])
        actual = quantize_values(values, [1, 6])
        expected = np.array([1, 1, np.nan, 6, 1, np.nan, 6])
        np.testing.assert_array_equal(actual, expected)

    @staticmethod
    def test_quantize_nulls_3d():
        """test"""
        values = np.array(
            [
                [2, 2, np.nan, 5, 2, np.nan, 4],
                [2, 2, np.nan, 5, 2, np.nan, 4],
                [np.nan, 2, np.nan, 5, 2, np.nan, 4],
            ]
        )
        actual = quantize_values(values, [1, 6])
        expected = np.array(
            [
                [1, 1, np.nan, 6, 1, np.nan, 6],
                [1, 1, np.nan, 6, 1, np.nan, 6],
                [np.nan, 1, np.nan, 6, 1, np.nan, 6],
            ]
        )
        np.testing.assert_array_equal(actual, expected)

    @staticmethod
    def test_quantize_series():
        """test"""
        values = pd.Series([2, 2, np.nan, 5, 2, np.nan, 4])
        index = np.arange(len(values))[::-1]
        values.index = index
        actual = quantize_values(values, [1, 6])
        expected = pd.Series([1, 1, np.nan, 6, 1, np.nan, 6], index=index)
        pd.testing.assert_series_equal(actual, expected)


if __name__ == "__main__":
    unittest.main()
