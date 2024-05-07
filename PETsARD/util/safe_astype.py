import logging
from typing import Union

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
    is_string_dtype,
)

from PETsARD.util.safe_dtype import safe_dtype


logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w',
                    format='[%(levelname).1s %(asctime)s] %(message)s',
                    datefmt='%Y%m%d %H:%M:%S')

def safe_astype(
    col: pd.Series,
    declared_dtype: Union[
        str,
        type,
        np.dtype,
        pd.CategoricalDtype,
        pd.IntervalDtype,
        pd.PeriodDtype,
        pd.SparseDtype
    ],
) -> pd.Series:
    """
    Safely cast a pandas Series to a given dtype.
    """
    # convert every dtype to safe string
    data_dtype: str = safe_dtype(col.dtype)
    declared_dtype: str = safe_dtype(declared_dtype)

    colname: str = 'unknown'
    if col.name is not None:
        colname = col.name

    is_change_dtype: bool = False
    if is_float_dtype(data_dtype) \
            and is_integer_dtype(declared_dtype):
        col = col.round()
        is_change_dtype = True
    elif is_integer_dtype(data_dtype) \
            and is_float_dtype(declared_dtype):
        is_change_dtype = True
    elif isinstance(declared_dtype, pd.CategoricalDtype) \
            or is_object_dtype(declared_dtype):
        is_change_dtype = True
    elif is_datetime64_any_dtype(declared_dtype) \
            and (is_float_dtype(data_dtype)
                or is_integer_dtype(data_dtype)
            ):
        is_change_dtype = True
    else:
        if data_dtype != declared_dtype:
            raise TypeError(
                f'The data type of {colname} is {data_dtype}, ' +
                f'which is not aligned with the metadata: {declared_dtype}.'
            )

    if is_change_dtype:
        col = col.astype(declared_dtype)

        logging.info(
            f'{colname} changes data dtype from ' +
            f'{data_dtype} to {declared_dtype} ' +
            'for metadata alignment.',
        )

    return col