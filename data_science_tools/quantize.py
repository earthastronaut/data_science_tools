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
        (nparray[Float]): Array same as values but quantized to the centers.
    """
    centers = get_quantize_centers(values, centers)
    midpoints = (centers[1:] + centers[:-1]) * 0.5
    idx = np.digitize(values, midpoints)
    return centers[idx]


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
        """Test quantize values"""
        quantize = np.array([-5, 2, 10])
        values = np.array([-10, -4, 1, 1, 1, 20, 5, 5.9, 7, 7, 16, 17])
        solution = np.array([-5, -5, 2, 2, 2, 10, 2, 2, 10, 10, 10, 10])
        self.assertTrue(np.all(quantize_values(values, quantize) == solution))


if __name__ == "__main__":
    unittest.main()
