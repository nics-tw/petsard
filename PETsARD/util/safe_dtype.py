from typing import Union

import numpy as np
import pandas as pd


def safe_dtype(
    dtype: Union[
        str,
        type,
        np.dtype,
        pd.CategoricalDtype,
        pd.IntervalDtype,
        pd.PeriodDtype,
        pd.SparseDtype
    ]
) -> str:
    """
    Convert various data type representations to a string representation.

    Args:
        dtype (
            str | np.dtype | type |
            pd.CategoricalDtype |
            pd.IntervalDtype | pd.PeriodDtype |
            pd.SparseDtype
        ): The data type to be converted.

    Returns:
        (str): The string representation of the input data type.

    Raises:
        TypeError: If the input data type is not supported.
    """
    if isinstance(dtype, np.dtype):
        return dtype.name
    elif isinstance(dtype, type):
        return dtype.__name__.lower()
    elif isinstance(dtype, pd.CategoricalDtype):
        return 'category'
    elif isinstance(dtype, pd.IntervalDtype):
        return f"interval[{dtype.subtype}]"
    elif isinstance(dtype, pd.PeriodDtype):
        return f"period[{dtype.freq}]"
    elif isinstance(dtype, pd.SparseDtype):
        return f"Sparse[{dtype.subtype}]"
    elif isinstance(dtype, str):
        return dtype.lower()
    else:
        raise TypeError(f'Unsupported data type: {dtype}')
