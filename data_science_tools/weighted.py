"""
Library to compute weighted quantiles, including the weighted median, of
numpy arrays.
"""
import numpy as np

__version__ = "0.3"

__all__ = [
    'quantile_1d',
    'quantile',
    'median',
    'mean'
]


def quantile_1d(data, weights, quantile_limit):
    """ Compute the weighted quantile of a 1D numpy array.

    Parameters:
        data : ndarray
            Input array (one dimension).
        weights : ndarray
            Array with the weights of the same size of `data`.
        quantile_limit : float
            Quantile to compute. It must have a value between 0 and 1.

    Returns:
        quantile_1d : float
            The output value.
    """
    data = np.asarray(data)
    weights = np.asarray(weights)
    if data.ndim != 1:
        raise TypeError("data must be a one dimensional array")

    if data.shape != weights.shape:
        raise TypeError("the length of data and weights must be the same")

    if not 0.0 <= quantile_limit <= 1.0:
        raise ValueError("quantile must have a value between 0.0 and 1.0")

    # Sort the data
    ind_sorted = np.argsort(data)
    sorted_data = data[ind_sorted]
    notnan = ~np.isnan(sorted_data)
    if np.count_nonzero(notnan) == 0:
        return np.nan

    sorted_weights = np.nan_to_num(weights[ind_sorted][notnan])

    # Compute the auxiliary arrays
    cuml_weights = np.cumsum(sorted_weights)

    # TO DO: Check that the weights do not sum zero
    prob_normalized = (
        (cuml_weights - 0.5 * sorted_weights) / np.sum(sorted_weights)
    )

    # Get the value of the weighted median
    return np.interp(quantile_limit, prob_normalized, sorted_data[notnan])


def quantile(data, weights, quantile_limit):
    """ Weighted quantile of an array with respect to the last axis.

    Parameters:
        data : ndarray
            Input array.
        weights : ndarray
            Array with the weights. It must have the same size of the last
            axis of `data`.
        quantile_limit : float
            Quantile to compute. It must have a value between 0 and 1.

    Returns:
        quantile : float
            The output value.

    """
    data = np.asarray(data)
    # TO DO: Allow to specify the axis
    if data.ndim == 0:
        raise TypeError("data must have at least one dimension")

    elif data.ndim == 1:
        return quantile_1d(data, weights, quantile_limit)

    # elif data.ndim > 1:
    shape = data.shape
    imr = data.reshape((np.prod(shape[:-1]), shape[-1]))
    result = np.apply_along_axis(
        quantile_1d, -1, imr, weights, quantile_limit)
    return result.reshape(shape[:-1])


def median(data, weights):
    """ Weighted median of an array with respect to the last axis.

    Alias for `quantile(data, weights, 0.5)`.
    """
    return quantile(data, weights, 0.5)


def mean(data, weights, **kws):
    """ Weighted mean

    Alias for `np.average(data, weights=weights, **kws)`
    """
    return np.average(data, weights=weights, **kws)
