from typing import Union

import numpy as np
from numpy.core._dtype import _kind_name
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
    dtype_name: str = ''

    if isinstance(dtype, np.dtype):
        dtype_name = dtype.name
    elif isinstance(dtype, pd.CategoricalDtype):
        # Category:
        #   TypeError: data type 'categorical' not understood
        # see abbreviation (e.g. 'O") by .kind
        dtype_name = f"category[{_kind_name(dtype.categories.dtype)}]"
    elif isinstance(dtype, pd.IntervalDtype):
        dtype_name = f"interval[{dtype.subtype}]"
    elif isinstance(dtype, pd.PeriodDtype):
        dtype_name = dtype.name # e.g. 'period[D]'
    elif isinstance(dtype, pd.SparseDtype):
        dtype_name = dtype.name # e.g. Sparse[float32, nan]
    elif isinstance(dtype, str):
        dtype_name = dtype
    elif isinstance(dtype, type):
        dtype_name = dtype.__name__.lower()
        if not (dtype_name == 'str'
            or dtype_name.startswith('int')
            or dtype_name.startswith('float')
        ):
            raise TypeError(f"Unsupported data type: {dtype_name}")
    else:
        raise TypeError(f"Unsupported data type: {dtype}")

    return dtype_name.lower()
