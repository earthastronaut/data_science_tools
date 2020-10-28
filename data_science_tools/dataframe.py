""" Tools for interacting with pandas DataFrames
"""
# pylint: disable=invalid-name
import pandas as pd
import numpy as np

__all__ = [
    "coalesce",
    "display_df",
    "drop_tmp_columns",
    "outer_join",
    "sizeof_df",
    "memory_usage_of_df",
    "merge_on_index",
    "window_function",
    "apply_row_number",
    "apply_series_method",
    "apply_window_func",
]


def coalesce(series):
    """Coalesce across many series getting the first value for each.

    Parameters
        series (Union[List, pd.DataFrame]): The series to combine or a
            dataframe of series.

    Returns
        pd.Series: Returns pandas series.
    """
    if isinstance(series, pd.DataFrame):
        series_iter = (series.iloc[:, i] for i in range(len(series.columns)))
    else:
        series_iter = iter(series)
    result = next(series_iter).copy()
    for s in series_iter:
        result = result.combine_first(s)
    return result


def merge_on_index(dataframes, preserve_index_order=True, **kws):
    """Merge dataframes on index.

    Can modify to merge all dataframes on another column but by default it uses index.

    Parameters
        dataframes (List[pd.DataFrame]): All the dataframes to merge.
        preserve_index_order (bool): Uses hashing which is unordered by default.
        When True this will concantenate the index in order of dataframes.
        **kws: passed to pd.merge(df[i], df[i+1], **kws) with defaults
        to {'how': 'outer', 'left_index': True', 'right_index': True}

    Returns
        pd.DataFrame: merged result.

    """
    kws_merge = {
        "how": "outer",
        "left_index": True,
        "right_index": True,
    }
    kws_merge.update(**kws)

    dataframes_iter = iter(dataframes)

    df = next(dataframes_iter).copy()
    if isinstance(df, np.ndarray):
        if df.ndim not in [1, 2]:
            raise ValueError(f"arrays must be <= 2d not {df.ndim}")
        df = pd.DataFrame(df)
        all_index = [df.index]
        for df_right in dataframes_iter:
            df_right = pd.DataFrame(df_right)
            df = pd.merge(df, df_right, **kws_merge)
            all_index.append(df_right.index)
    else:
        all_index = [df.index]
        for df_right in dataframes_iter:
            df = pd.merge(df, df_right, **kws_merge)
            all_index.append(df_right.index)

    if preserve_index_order:
        index = pd.Index(np.concatenate(all_index))
        index = index[~index.duplicated()]
        # materialize the view of frame. Garbage collector should remove the
        # intermediate ones.
        return df.loc[index].copy()
    else:
        return df


def display_df(df, style=None, max_rows=100, **kws):
    """Display pandas dataframe

    display(HTML(df.to_html(**kws)))
    """
    # ipython is only used for this function
    from IPython.display import (  # pylint: disable=import-outside-toplevel
        display,
        HTML,
    )

    kws["max_rows"] = max_rows
    sty = df.style
    if style is not None:
        sty.ctx = style.ctx
    display(HTML(sty.render(**kws)))


def drop_tmp_columns(df, tmp_prefix="tmp_"):
    """Drop any columns in-place starting with <tmp_prefix>"""
    columns = [c for c in df.columns if c.startswith(tmp_prefix)]
    df.drop(columns=columns, inplace=True)


def indexer(x, bins):
    """Get the index for the centers

    centers = (bins[1:] + bins[:-1]) * 0.5
    This centers np.digitize to be actual indexes for the centers

    """
    digit = np.digitize(x, bins=bins) - 1
    return np.ma.masked_inside(digit, 0, len(bins) - 2)


def in1d(series1, series2):
    """Returns a pandas.Series which uses np.in1d"""
    return pd.Series(np.in1d(series1, series2), index=series1.index)


def outer_join(dataframe1, dataframe2):
    """Perform OUTER JOIN dataframe1 and dataframe2

    Parameters
        dataframe1 (DataFrame): First data frame.
        dataframe2 (DataFrame): Second data frame.

    Returns
        DataFrame: Returns a dataframe with columns from both.

    """
    # TO DO: add inner keys for the outer join
    key = "join_key_for_cartesian_product_with_obscure_uniqueness"
    dataframe1[key] = 1
    dataframe2[key] = 1

    prod = pd.merge(dataframe1, dataframe2, on=key)

    del prod[key]
    del dataframe1[key]
    del dataframe2[key]
    return prod


def sizeof_df(num, size_qualifier=""):
    """ returns size in human readable format """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f%s %s" % (num, size_qualifier, x)
        num /= 1024.0
    return "%3.1f%s %s" % (num, size_qualifier, "PB")


def memory_usage_of_df(df, deep=False):
    """ Returns the memory usage of a dataframe """
    is_approximate_sizeof = not deep and (
        "object" in df.get_dtype_counts() or pd.api.types.is_object_dtype(df.index)
    )
    size_qualifier = "+" if is_approximate_sizeof else ""
    mem_usage = df.memory_usage(index=True, deep=deep).sum()
    return sizeof_df(mem_usage, size_qualifier)


# ####################### WINDOW FUNCTION ####################### #


def get_window_range(length, preceding, following, include_incomplete=True):  # noqa
    """Generator for the window range

    Paremters:
        length (int): Maximum length
        preceding (int): Number preceding in index, inclusive
        following (int): Number following the index, exclusive
        include_incomplete (bool):
            If False then will return None for preceding and
            following outside of the [0, length) range

    Yields:
        (int, int, int): the preceding index, current index, following index
    """
    # TO DO: test error (10, -1, None)
    # TO DO: test include_incomplete
    if preceding is not None:
        if not isinstance(preceding, int):
            raise TypeError(f"preceding must be int not {type(preceding)}")
    if following is not None:
        if not isinstance(following, int):
            raise TypeError(f"preceding must be int not {type(following)}")

    p = 0
    f = length
    for i in range(length):
        if preceding is None:
            p = 0
        else:
            p = i - preceding
            if not include_incomplete and p < 0:
                p = None
            else:
                p = min(max(0, p), length)

        if following is None:
            f = length
        else:
            f = i + following
            if not include_incomplete and f > length:
                f = None
            else:
                f = max(min(f, length), 0)
        if p is not None and f is not None and (p > f):
            raise ValueError(
                f"Preceding index larger than following, {p} >= {f} and can't "
                f"do df.iloc[{p}:{f}]"
            )
        yield p, i, f


def apply_window_func(
    df,
    apply,
    apply_kws=None,
    apply_full_window=False,
    order_by=None,
    order_ascending=True,
    preceding=None,
    following=None,
):  # pylint: disable=too-many-locals
    """Order the dataframe, apply the function"""
    if order_by is None:
        df_ordered = df
    else:
        # TO DO: can you sort without copying dataframe?
        df_ordered = df.sort_values(order_by, ascending=order_ascending)

    apply_kws = apply_kws or {}
    results = []
    # TO DO: include_incomplete and handle p is None and f is None
    for window in get_window_range(len(df_ordered), preceding, following):
        p, _, f = window
        if apply_full_window:
            value = apply(df_ordered, window, **apply_kws)
        else:
            value = apply(df_ordered.iloc[p:f], **apply_kws)
        results.append(value)

    # TO DO: if results is Series?
    # TO DO: index + results = Series
    r = pd.Series(results, index=df_ordered.index)
    return r


def apply_series_method(df, column, method, **method_kws):
    """This window function selects a column and calls a method on that Series.

    Parameters:
        df (DataFrame): pandas dataframe
        column (str): Column to select from the dataframe
        method (str): Method to call on the the selected Series.
        **method_kws: Passed to the method

    Returns:
       any: result of getattr(df[column], method)(**method_kws)


    """
    agg = getattr(df[column], method)
    return agg(**method_kws)


def apply_row_number(df_ordered, window):  # pylint: disable=unused-argument
    """ROW_NUMBER Window Function

    Determines the ordinal number of the current row within a group of rows,
    counting from 1, based on the ORDER BY expression in the OVER clause. If
    the optional PARTITION BY clause is present, the ordinal numbers are reset
    for each group of rows. Rows with equal values for the ORDER BY expressions
    receive the different row numbers nondeterministically.

    https://docs.aws.amazon.com/redshift/latest/dg/r_WF_ROW_NUMBER.html

    """
    _, i, _ = window
    return int(i + 1)


def _resolve_apply_function(apply, apply_kws, apply_full_window):
    """Does some fancy overloading for apply because sometimes I want to
    just call window_function(df, 'row_number', partition_by='')

    """
    if isinstance(apply, str):
        name = str(apply)

        if name == "rank":
            raise NotImplementedError(
                "Rank not implemented\n"
                "https://docs.aws.amazon.com/redshift/latest/dg/r_WF_RANK.html"
            )
            # return apply_rank, apply_kws, True

        if name == "dense_rank":
            raise NotImplementedError(
                "Dense Rank not implemented\n"
                "https://docs.aws.amazon.com/redshift/latest/dg/r_WF_DENSE_RANK.html"
            )
            # return apply_rank, apply_kws, True

        elif name == "row_number":
            return apply_row_number, apply_kws, True

        else:
            kws = {
                "method": name,
            }
            # window(df, 'mean', 'column1')
            if isinstance(apply_kws, str):
                kws["column"] = apply_kws
            # window(df, 'quantile', {'column': 'column1', 'q': 0.5})
            elif isinstance(apply_kws, dict):
                kws.update(apply_kws)

            return apply_series_method, kws, False
    else:
        # pass through
        return apply, apply_kws, apply_full_window


def window_function(
    df,
    apply,
    apply_kws=None,
    partition_by=None,
    order_by=None,
    order_ascending=True,
    preceding=0,
    following=1,
    apply_full_window=False,
):  # pylint: disable=too-many-locals
    """Apply a window function to the dataframe similar to redshift window functions

    ```
    SELECT
       df.index
       , apply(expression) OVER (PARTITION BY partition_by ORDER BY order_by BETWEEN preceding PRECEDING AND following FOLLOWING)
    FROM df
    ```

    Function signatures for different window function calls. Based on
    [Redshift Window Function Syntax](https://docs.aws.amazon.com/redshift/latest/dg/r_Window_function_synopsis.html).

    ```
    SELECT
      df.index

      -- window_function(df, apply)
      , apply(...) OVER ()

      -- window_function(df, apply, order_by='column1')
      , apply(...) OVER (ORDER BY column1)

      -- window_function(df, apply, order_by=['column1', 'column2'])
      , apply(...) OVER (ORDER BY column1, column2)

      -- window_function(df, apply, order_by='column1', order_ascending=False)
      , apply(...) OVER (ORDER BY column1 DESC)

      -- window_function(df, apply, order_by='column1', preceding=None)
      , apply(...) OVER (ORDER BY column1 ROWS UNBOUNDED PRECEDING )

      -- window_function(df, apply, order_by='column1', preceding=5)
      , apply(...) OVER (ORDER BY column1 ROWS 5 PRECEDING )

      -- window_function(df, apply, order_by='column1', following=None)
      , apply(...) OVER (ORDER BY column1 BETWEEN CURRENT_ROW AND UNBOUNDED FOLLOWING)

      -- window_function(df, apply, order_by='column1', preceding=None, following=None)
      , apply(...) OVER (ORDER BY column1 BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)

      -- window_function(df, apply, order_by='column1', preceding=2, following=3)
      , apply(...) OVER (ORDER BY column1 BETWEEN 2 PRECEDING AND 2 FOLLOWING)
      # TO DO: CHECK THIS FOR FOLLOWING

      -- window_function(df, apply, partition_by='column3')
      , apply(...) OVER (PARTITION BY column3)

      -- window_function(df, apply, partition_by=['column3', 'column4'])
      , apply(...) OVER (PARTITION BY column3, column4)

      -- window_function(df, apply, partition_by=['column3', 'column4'], order_by='column1')
      , apply(...) OVER (PARTITION BY column3, column4 ORDER BY column1)

    FROM df
    ```



    Short cut for some functions
    ```
    SELECT
        -- window_function(df, 'mean', 'column1', partition_by='column2')
        AVG(column1) OVER (PARTITION BY column2)

        -- window_function(df, 'quantile', {'column': 'column1', 'q': 0.5}, partition_by='column2', order_by='column3')
        , PERCENTILE(0.5, column1) OVER (PARTITION BY column2 ORDER BY column3)

        -- window_function(df, 'row_number', partition_by='column2', order_by='column3')
        , ROW_NUMBER() OVER (PARITION BY column2 ORDER BY column3)

    FROM df
    ```


    Parameters:
        apply (function): Apply this function to the window
        apply_kws (dict): Apply these keywords to the function
        partition_by (None or str): column(s) to partition by
        order_by (None or str): column(s) to order by
        order_ascending (bool): Order ASC or DESC

        preceding (None or int): current_row - preceding
            - None: unbound state
            - 0: current row, inclusive
            - int: number of preceeding rows, inclusive if index. Can use negative values.

        following (None or int): current_row + following
            - None: unbound state
            - 0: excludes current row
            - int: number of preceeding row, exclusive of index

    Returns:
        Series: Results of applying the window function

    Notes:

        * index order not preserved. When using order_by, the order of the
        index is not preserved in the output. Example: df.index = [1, 2, 3]
        the result may have index=[2, 3, 1] depending on the ordering of the
        order_by values.

        * preceding and following. The window is based on preceding and following and current row index.
        Particularly the index for any row is, df.iloc[current_row - preceding: current_row + following].
        The following is exclusive based on slice.

    """  # pylint: disable=line-too-long # noqa
    # TODO: test apply functions which return lists or Series. Can apply act on
    # multiple columns at once.
    # TODO: order_nulls_first=True
    apply, apply_kws, apply_full_window = _resolve_apply_function(
        apply, apply_kws, apply_full_window
    )

    kws = dict(
        apply=apply,
        apply_kws=apply_kws,
        order_by=order_by,
        order_ascending=order_ascending,
        preceding=preceding,
        following=following,
        apply_full_window=apply_full_window,
    )

    if partition_by is None:
        results_series = apply_window_func(df, **kws)
    else:
        # TO DO: better way instead of .apply? which more performant?
        results = df.groupby(partition_by).apply(apply_window_func, **kws)

        # TO DO: Better way which still preserves index
        results_index_names = results.index.names
        surrogate_names = [f"_surrogate_{i}" for i in range(len(results_index_names))]
        results.index.names = surrogate_names

        # parition_by is passed through GroupBy to
        # pandas.core.groupby.grouper._get_grouper as key
        key = partition_by
        if not isinstance(key, list):
            keys = [key]
        else:
            keys = key
        num_keys = len(keys)
        surrogate_index = surrogate_names[num_keys:]

        # TO DO: how to reindex to remove unneeded index but
        # still check that the index is unique. This is inefficient.
        results_series = (
            # results is a series, MultiIndex = [partition_by] + [index]
            results
            # unstack all, unfortunately makes a copy
            .reset_index()
            # restack just the [index] values
            .set_index(surrogate_index)
            # select the last column which is the values
            .iloc[:, -1]
        )
        results_series.index.names = results_index_names[num_keys:]
        results_series.name = results.name

    return results_series
