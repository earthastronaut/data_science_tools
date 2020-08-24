""" Tests for dataframe module
"""
# pylint: disable=missing-function-docstring,invalid-name

import unittest

import numpy as np
import pandas as pd

from data_science_tools import statistics


class TestBootstrap(unittest.TestCase):
    """ Test bootstrap helper """

    def test_bootstrap_null(self):
        def func(_, a, b=1):
            return a + b
        data = np.ones(10)
        results = statistics.bootstrap(
            data, func, func_args=(1, ), func_kws={'b': 1},
            bootstrap_iterations=5,
        )
        self.assertListEqual(results, [2 for _ in range(5)])

    def test_bootstrap_simple_mean(self):
        data = np.ones(10)
        results = statistics.bootstrap(
            data, np.mean,
            bootstrap_iterations=5,
        )
        self.assertListEqual(results, [1 for _ in range(5)])

    def test_bootstrap_min_sample_size_choice(self):
        data = np.ones(100)
        results = statistics.bootstrap(
            data, len,
            bootstrap_min_sample_size=3,
            bootstrap_iterations=10,
            sample_method='choice',
        )
        for i in range(10):
            self.assertTrue(results[i] >= 3, f'{i} has length {results[i]}')

    def test_bootstrap_min_sample_size_integer(self):
        data = np.ones(100)
        results = statistics.bootstrap(
            data, len,
            bootstrap_min_sample_size=3,
            bootstrap_iterations=10,
            sample_method='integer',
        )
        for i in range(10):
            self.assertTrue(results[i] >= 3, f'{i} has length {results[i]}')

    def test_bootstrap_sample_size(self):
        data = np.ones(10)
        results = statistics.bootstrap(
            data, len,
            bootstrap_sample_size=5,
            bootstrap_iterations=2,
        )
        for i in range(2):
            self.assertTrue(results[i] == 5, f'{i} has length {results[i]}')

    def test_bootstrap_sample_size_fraction(self):
        data = np.ones(10)
        results = statistics.bootstrap(
            data, len,
            bootstrap_sample_size=0.5,
            bootstrap_iterations=2,
        )
        for i in range(2):
            self.assertTrue(results[i] == 5, f'{i} has length {results[i]}')

    def test_bootstrap_custom_sampler(self):
        data = np.arange(10)
        def sample_method(_, number):
            return np.arange(0, number)

        results = statistics.bootstrap(
            data, np.mean,
            bootstrap_sample_size=5, # select first 5 every time
            bootstrap_iterations=4, # number of iteractions
            sample_method=sample_method,
        )
        # first three are [0, 1, 2, 3, 4] so mean is 2
        self.assertListEqual(results, [2 for _ in range(4)])

    def test_bootstrap_stats(self):
        def func(_):
            return np.arange(3)
        result = statistics.bootstrap_stats(
            np.ones(10), func,
        )
        expected = pd.DataFrame(
            np.array([
                [0, 1, 2],
                [0, 1, 2],
                [0, 1, 2],
                [0, 0, 0],
                [0, 1, 2],
                [0, 1, 2],
            ]).T,
            columns=[
                'p10',
                'p50',
                'p90',
                'std',
                'mean',
                'y',
            ]
        )
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)
