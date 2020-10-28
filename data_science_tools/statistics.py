""" Tools to bootstrap function results and errors.
"""
import pandas as pd
import numpy as np


__all__ = [
    "bootstrap",
    "bootstrap_stats",
]


def bootstrap(
    data,
    func,
    func_args=None,
    func_kws=None,
    bootstrap_iterations=100,
    bootstrap_sample_size=0.75,
    bootstrap_min_sample_size=5,
    sample_method="choice",
):
    """Bootstrap a sample.

    Randomly samples from x along axis=0, and apply a function for some number
    of iterations

    return [func(x[sample_idx]) for _ in range(bootstrap_iterations)]

    Parameters
        data (array-like or DataFrame): This is used to sample from along axis=0
            If it's a Pandas Dataframe then m.iloc[idx] where idx are the
            integers used for sampling.
        func (callable): callable function whose first argument is data.
        func_args (tuple): passed to func(m, *func_args, **func_kws)
        func_kws (dict): passed to func(m, *func_args, **func_kws)
        bootstrap_iterations (int): number of iterations to bootstrap
        bootstrap_sample_size (float or int):
            if integer then samples that number from the total
            if float less then 1.0 it samples that fraction of the total
        bootstrap_min_sample_size (int): will error with less than this
            many measurements
        sample_method ('choice', 'integer', callable): How to randomly sample
            * 'choice':
                * np.random.choice(np.arange(length), number, replace=False)
                * always returns correct sample size but takes longer to eval
            * 'integer':
                * np.unique(np.random.randint(0, length, number))
                * faster evaluation but will give < number desired
            * callable:
                * calls this function to return the index of sample
                * callable(length: int, number: int)

    Returns
        list[func(m, *func_args, **func_kws)] : A list of the results of
            evaluating the function <bootstrap_iterations> times with a
            random sampling of <bootstrap_sample_size>
    """

    length = len(data)
    if bootstrap_sample_size < 1.0:
        number = int(length * bootstrap_sample_size)  # sample_size
    else:
        number = int(bootstrap_sample_size)

    # if the number requested is larger than the length just return all the
    # indicies
    if number >= length:
        raise ValueError("sample size is larger then length")
    elif number < bootstrap_min_sample_size:
        raise ValueError("sample size is too small")
    if not callable(sample_method) and sample_method not in ("choice", "integer"):
        raise ValueError("sample_method should be 'choice' or 'integer'")

    func_args = func_args or []
    func_kws = func_kws or {}

    bootstrap_results = []
    for _ in range(bootstrap_iterations):
        # decide which method to use
        if sample_method == "choice":
            idx = np.random.choice(np.arange(length), number, replace=False)
        elif sample_method == "integer":
            idx = np.unique(np.random.randint(0, length, number))
        elif callable(sample_method):
            idx = sample_method(length, number)

        if isinstance(data, (pd.DataFrame, pd.Series)):
            res = func(data.iloc[idx], *func_args, **func_kws)
        else:
            res = func(data[idx], *func_args, **func_kws)

        bootstrap_results.append(res)

    return bootstrap_results


def bootstrap_stats(data, func, *args, **kwargs):
    """Runs bootstrap function and then compiles the results in aggregate.

    Parameters
        data (array-like or DataFrame): This is used to sample from along axis=0
            If it's a Pandas Dataframe then m.iloc[idx] where idx are the
            integers used for sampling.
        func (callable): callable function whose first argument is data.
        *args, **kwargs: passed to bootstrap function

    Returns
        DataFrame: aggregate metrics of bootstrap results.
    """
    kwargs["func"] = func
    try:
        bootstrap_results = pd.DataFrame(bootstrap(data, *args, **kwargs))
    except ValueError:
        return pd.DataFrame()

    func_args = kwargs.get("func_args", [])
    func_kws = kwargs.get("func_kws", {})

    return pd.DataFrame(
        {
            "p10": bootstrap_results.dropna().quantile(0.1),
            "p50": bootstrap_results.dropna().quantile(0.5),
            "p90": bootstrap_results.dropna().quantile(0.9),
            "std": bootstrap_results.std(),
            "mean": bootstrap_results.mean(),
            "y": func(data, *func_args, **func_kws),
        }
    )
