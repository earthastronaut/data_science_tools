""" Tests for dataframe module
"""
# pylint: disable=missing-function-docstring,invalid-name,no-self-use

import unittest

import pandas as pd
import numpy as np

from data_science_tools import dataframe

merge_on_index = dataframe.merge_on_index


class TestWindowFunction(unittest.TestCase):
    """ Test window_functions """
    def _generate_example(self, size=10):
        df_test = pd.DataFrame()
        df_test['name'] = pd.np.random.choice(['tom', 'bob'], size)
        df_test['height'] = pd.np.random.randint(45, 60, size)
        return df_test

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)

        self.df_example_1 = pd.DataFrame(
            [('bob', 45),
             ('bob', 58),
             ('tom', 46),
             ('bob', 55),
             ('tom', 53),
             ('bob', 54),
             ('bob', 45),
             ('tom', 55),
             ('bob', 53),
             ('bob', 51)],
            columns=['name', 'height'],
        )
        self.df_example_1.index += 10

        self.df_example_2 = pd.DataFrame(
            [('bob', 'smith', 45),
             ('bob', 'jones', 50),
             ('tom', 'smith', 53),
             ('bob', 'jones', 50),
             ('bob', 'jones', 58),
             ('tom', 'jones', 47),
             ('bob', 'smith', 54),
             ('bob', 'jones', 48),
             ('tom', 'smith', 59),
             ('tom', 'smith', 49)],
            columns=['first_name', 'last_name', 'height']
        )

        # MultiIndex
        self.df_example_3 = self.df_example_2.copy()
        self.df_example_3.index = pd.MultiIndex.from_tuples(
            [
                ('developer', 30),
                ('developer', 31),
                ('developer', 32),
                ('developer', 33),
                ('programmer', 40),
                ('programmer', 41),
                ('programmer', 42),
                ('programmer', 43),
                ('programmer', 44),
                ('programmer', 45)],
            names=['occupation', 'age']
        )

    def _apply_example_1_height_mean(self, df):
        return df['height'].mean()

    def test_apply_full_range(self):
        results = dataframe.window_function(
            self.df_example_1,
            self._apply_example_1_height_mean,
            preceding=None, following=None,
        )

        answer = pd.Series(51.5, index=self.df_example_1.index)
        pd.testing.assert_series_equal(answer, results)

    def test_apply_current(self):
        results = dataframe.window_function(
            self.df_example_1,
            self._apply_example_1_height_mean,
        )
        answer = self.df_example_1['height'].astype(float)
        answer.name = None
        pd.testing.assert_series_equal(answer, results)

    def test_apply_row_number(self):
        results = dataframe.window_function(
            self.df_example_1,
            'row_number',
            order_by='height',
        )
        answer = pd.Series(
            [1, 10, 3, 8, 5, 7, 2, 9, 6, 4],
            index=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        )

        # TO DO fix result index
        results.sort_index(inplace=True)
        pd.testing.assert_series_equal(answer, results)

    def test_apply_series_method(self):
        example_data = pd.DataFrame()
        example_data['column1'] = [
            2, 4, 6,
            8, 10, 12
        ]

        results = dataframe.window_function(
            example_data,
            'mean', 'column1',
        )
        answer = example_data['column1'].astype(float)
        answer.name = None
        pd.testing.assert_series_equal(answer, results)

    def test_apply_row_number_partition(self):
        results = dataframe.window_function(
            self.df_example_1,
            'row_number',
            partition_by='name',
            order_by='height',
        )
        answer = pd.Series(
            [1, 7, 1, 6, 2, 5, 2, 3, 4, 3],
            index=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        )
        # ordering causes results to be in random order
        answer.sort_index(inplace=True)
        results.sort_index(inplace=True)
        pd.testing.assert_series_equal(answer, results)

    def test_apply_row_number_partition_multiple(self):
        results = dataframe.window_function(
            self.df_example_2,
            'row_number',
            partition_by=['first_name', 'last_name'],
            order_by='height',
        )
        answer = pd.Series(
            [1, 2, 3, 4, 1, 2, 1, 1, 2, 3],
            index=[7, 1, 3, 4, 0, 6, 5, 9, 2, 8]
        )
        # ordering causes results to be in random order
        answer.sort_index(inplace=True)
        results.sort_index(inplace=True)
        pd.testing.assert_series_equal(answer, results)

    def test_apply_row_number_partition_multindex(self):
        results = dataframe.window_function(
            self.df_example_3,
            'row_number',
            partition_by=['first_name', 'last_name'],
            order_by='height',
        )

        answer = pd.Series(
            [1, 2, 3, 4, 1, 2, 1, 1, 2, 3],
        )
        answer.index = pd.MultiIndex.from_tuples(
            [('programmer', 43),
             ('developer', 31),
             ('developer', 33),
             ('programmer', 40),
             ('developer', 30),
             ('programmer', 42),
             ('programmer', 41),
             ('programmer', 45),
             ('developer', 32),
             ('programmer', 44)],
            names=['occupation', 'age']
        )
        answer.sort_index(inplace=True)
        results.sort_index(inplace=True)
        pd.testing.assert_series_equal(answer, results)

    def test_preceding_inclusive_following_exclusive(self):
        example_data = pd.DataFrame()
        example_data['column1'] = [
            2, 4, 6, 8, 10, 12
        ]

        def apply(df):
            return df['column1'].mean()

        results = dataframe.window_function(
            example_data, apply, preceding=2, following=2,
        )

        answer = pd.Series([
            3.,  # 0:2 -> [2, 4]
            4.,  # 0:3 -> [2, 4, 6]
            5.,  # 0:4 -> [2, 4, 6, 8]
            7.,  # 1:5 -> [4, 6, 8, 10]
            9.,  # 2:6 -> [6, 8, 10, 12]
            10.,  # 3:7 -> [8, 10, 12]
        ])
        pd.testing.assert_series_equal(answer, results)

    def test_preceding_and_following_offsets(self):
        example_data = pd.DataFrame()
        example_data['column1'] = [
            2, 4, 6,
            8, 10, 12
        ]

        results = dataframe.window_function(
            example_data, 'mean', 'column1',
            preceding=-1,
            following=4,
        )

        answer = pd.Series([
            6.,  # 1:4 -> [4, 6, 8]
            8.,  # 2:5 -> [6, 8, 10]
            10.,  # 3:6 -> [8, 10, 12]
            11.,  # 4:6 -> [10, 12]
            12.,  # 5:6 -> [12]
            float('nan'),  # 6:6 -> []
        ])
        pd.testing.assert_series_equal(answer, results)

    def test_preceding_and_following_offsets_error(self):
        example_data = pd.DataFrame()
        example_data['column1'] = [
            2, 4, 6,
            8, 10, 12
        ]
        with self.assertRaises(ValueError):
            dataframe.window_function(
                example_data, 'mean', 'column1',
                preceding=-4,
                following=2,
            )

    def test_unbounded_preceding(self):
        example_data = pd.DataFrame()
        example_data['column1'] = [
            2, 4, 6,
            8, 10, 12
        ]

        results = dataframe.window_function(
            example_data, 'mean', 'column1',
            preceding=None,
        )

        answer = pd.Series([
            2.,  # 0:1 -> [2]
            3.,  # 0:2 -> [2, 4]
            4.,  # 0:3 -> [2, 4, 6]
            5.,  # 0:4 -> [2, 4, 6, 8]
            6.,  # 0:5 -> [2, 4, 6, 8, 10]
            7.,  # 0:6 -> [2, 4, 6, 8, 10, 12]
        ])
        pd.testing.assert_series_equal(answer, results)


class TestMergeOnIndex(unittest.TestCase):

    def test_merge_on_index_base_case(self):
        # test data
        x = [0, 1, np.nan, 3, 4, 5, 6, 7, 8, 9]
        # test arbirary ordering, I ensured they are unique
        idx = [2, 15, 17, 8, 10, 12, 14, 16, 18, 20]
        np.testing.assert_equal(len(x), len(idx))
        dataframes = [
            pd.DataFrame({'a': x[:4]}, index=idx[:4]),
            pd.DataFrame({'b': x[2:5]}, index=idx[2:5]),
            pd.DataFrame({'c1': x[7:10], 'c2': x[0:3]}, index=idx[7:10])
        ]

        expected = pd.DataFrame(
            {
                'a': [0, 1, np.nan, 3, np.nan, np.nan, np.nan, np.nan],
                # test columns which overlap
                'b': [np.nan, np.nan, np.nan, 3, 4, np.nan, np.nan, np.nan],
                # test columns which are all nan
                'c1': [np.nan, np.nan, np.nan, np.nan, np.nan, 7, 8, 9],
                # test multiple columns merged
                'c2': [np.nan, np.nan, np.nan, np.nan, np.nan, 0, 1, np.nan],
            },
            index=idx[:5] + idx[7:10],
        )
        actual = merge_on_index(dataframes)
        pd.testing.assert_frame_equal(actual, expected)

    def test_merge_on_index_numpy_arrays(self):
        # test data
        x = [0, 1, np.nan, 3, 4, 5, 6, 7, 8, 9]
        dataframes = [
            np.array(x[:4]),
            np.array(x[:5]),
            np.array([x[:4], x[6:10]]).T,
        ]

        expected = pd.DataFrame(
            {
                '0_x': [0, 1, np.nan, 3, np.nan],
                '0_y': [0, 1, np.nan, 3, 4],
                # test columns which are all nan
                0: [0, 1, np.nan, 3, np.nan],
                1: [6, 7, 8, 9, np.nan],
            },
            index=[0, 1, 2, 3, 4],
        )
        actual = merge_on_index(dataframes)
        pd.testing.assert_frame_equal(actual, expected)


if __name__ == '__main__':
    unittest.main()
