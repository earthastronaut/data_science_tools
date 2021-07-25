""" Unit tests for weighted statistics
"""
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,no-self-use
# %%

import unittest

from data_science_tools import weighted


class TestWeighted(unittest.TestCase):
    """Unit tests for weighted statistics"""

    def test_weighted_mean_even_weights(self):
        actual = weighted.mean([1, 2, 3], [1, 1, 1])
        self.assertEqual(actual, 2.0)

    def test_weighted_mean_one_zero_weight(self):
        actual = weighted.mean([1, 2, 3], [0, 1, 1])
        self.assertEqual(actual, 2.5)

    def test_weighted_mean(self):
        actual = weighted.mean([1, 2, 5], [0, 0.5, 1])
        self.assertEqual(actual, 4.0)

    def test_median_even_weights(self):
        actual = weighted.median([1, 1, 2, 3, 3], [1, 1, 1, 1, 1])
        self.assertEqual(actual, 2.0)

    def test_median_with_zero_weights(self):
        actual = weighted.median([1, 1, 2, 3, 3], [0, 0, 1, 1, 1])
        self.assertEqual(actual, 3.0)


# %%

if __name__ == "__main__":
    unittest.main()
