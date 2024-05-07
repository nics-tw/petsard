import logging
from typing import Union

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
)

from PETsARD.util.optimize_dtypes import optimize_dtype
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
    NUMERIC_MAP: dict[str, int] = {
        'int8': 8,
        'int16': 16,
        'int32': 32,
        'int64': 64,
        'float32': 32,
        'float64': 64,
    }

    colname: str = 'unknown'
    if col.name is not None:
        colname = col.name

    is_change_dtype: bool = False
    opt_dtype: str = ''
    is_type_error: bool = False
    is_value_error: bool = False
    if is_integer_dtype(declared_dtype):
        if is_integer_dtype(data_dtype):
            opt_dtype = optimize_dtype(col)
            if NUMERIC_MAP[opt_dtype] < NUMERIC_MAP[declared_dtype]:
                is_change_dtype = True
            elif NUMERIC_MAP[opt_dtype] > NUMERIC_MAP[declared_dtype]:
                is_value_error = True
        elif is_float_dtype(data_dtype):
            col = col.round()
            is_change_dtype = True
        else:
            is_type_error = True
    elif is_float_dtype(declared_dtype):
        if declared_dtype == 'float16' \
            and (is_integer_dtype(data_dtype)
                or is_float_dtype(data_dtype)
            ):
            logging.info(
                f'declared dtype {declared_dtype} ' +
                'will changes to float32 ' +
                'for pandas only support float32 above.',
            )
            declared_dtype == 'float32'
            is_change_dtype = True
        elif is_integer_dtype(data_dtype):
            is_change_dtype = True
        elif is_float_dtype(data_dtype):
            opt_dtype = optimize_dtype(col)
            if NUMERIC_MAP[opt_dtype] < NUMERIC_MAP[declared_dtype]:
                is_change_dtype = True
            elif NUMERIC_MAP[opt_dtype] > NUMERIC_MAP[declared_dtype]:
                is_value_error = True
        else:
            is_type_error = True
    elif declared_dtype in ['category', 'object']:
        if declared_dtype == 'category' \
                and data_dtype == 'float16':
            logging.info(
                f'dtype {data_dtype} change to float32 first' +
                'for pandas only support float32 above.',
            )
            col = col.astype('float32')
        is_change_dtype = True
    elif declared_dtype.startswith('datetime') \
            and (is_float_dtype(data_dtype)
                or is_integer_dtype(data_dtype)
            ):
        is_change_dtype = True
    else:
        if data_dtype != declared_dtype:
            is_type_error = True

    if is_type_error:
        raise TypeError(
            f'The data type of {colname} is {data_dtype}, ' +
            f'which is not aligned with the metadata: {declared_dtype}.'
        )
    if is_value_error:
        raise ValueError(
            f'The data type of {colname} is {data_dtype}, ' +
            f'and the optimized data type is {opt_dtype}, ' +
            f'which is out of the range of the metadata: {declared_dtype}.'
        )

    if is_change_dtype:
        col = col.astype(declared_dtype)

        logging.info(
            f'{colname} changes data dtype from ' +
            f'{data_dtype} to {declared_dtype} ' +
            'for metadata alignment.',
        )

    return col