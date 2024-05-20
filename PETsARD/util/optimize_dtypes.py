from typing import Dict
import warnings

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from PETsARD.util.verify_column_types import verify_column_types
from PETsARD.util.params import (
    ALLOWED_COLUMN_TYPES,
    OPTIMIZED_DTYPES,
)
from PETsARD.error import ConfigError


def optimize_dtype(col_data: pd.Series) -> str:
    """
    Optimize the data type of a single column.

    Args:
        col_data (pd.Series): The column data to be optimized.

    Returns:
        str: The optimized data type for the column.
    """
    opt_dtype: str = ''
    if is_object_dtype(col_data):
        # If dtype from pandas is object, infer the optimized dtype
        # by trying to convert it to datetime.
        opt_dtype = _optimized_object_dtypes(col_data=col_data)
    elif is_numeric_dtype(col_data):
        # If dtype from pandas is numeric, infer the optimized dtype
        # by comparing the range of the column data
        # with the ranges of each numeric data type.
        opt_dtype = _optimized_numeric_dtypes(col_data=col_data)
    else:
        # Otherwise, keep the original dtype
        opt_dtype = col_data.dtype.name
    return opt_dtype

def optimize_dtypes(
    data: pd.DataFrame,
    column_types: Dict[str, list] = None
) -> Dict[str, str]:
    """
    Force setting discrete and datetime columns been load as str at first.

    Args:
        data (pd.DataFrame): The dataframe to be checked.
        column_types (dict): The column types to be forced assigned.

    Return:
        optimize_dtypes (dict):
            dtype: particular columns been force assign as string
    """
    original_dtypes = data.dtypes
    optimize_dtypes: Dict[str, str] = {}

    # 1. if column_types is setting, force assign dtype
    if column_types is not None:
        if not verify_column_types(column_types):
            raise ConfigError
        for coltype in ALLOWED_COLUMN_TYPES:
            if coltype in column_types:
                for colname in column_types[coltype]:
                    optimize_dtypes[colname] = OPTIMIZED_DTYPES[coltype]

    # 2. retrive remain columns not been assigned by column_types
    remain_col: list = list(
        set(original_dtypes.keys()) - set(optimize_dtypes.keys())
    )

    # 3. for remain columns
    for colname in remain_col:
        col_data: pd.Series = data[colname]
        optimize_dtypes[colname] = optimize_dtype(col_data)

    return optimize_dtypes


def _optimized_object_dtypes(col_data: pd.Series) -> str:
    """
    Determine the optimized column type for a given pandas Series of object dtype,
        by trying to convert it to datetime.
        - If any of it cannot be recognized as a datetime,
              then it will be recognized as a category.
        - Otherwise, it will be recognized as a datetime.

    Parameters:
        col_data (pd.Series): The pandas Series containing the column data.

    Returns:
        str: The optimized column type.
    """
    # if all data in column is NaN, force assign as category
    if col_data.isna().all():
        return OPTIMIZED_DTYPES['category']

    col_data.dropna(inplace=True)

    # ignore below UserWarning from pandas
    #   UserWarning: Could not infer format,
    #       so each element will be parsed individually, falling back to `dateutil`.
    #       To ensure parsing is consistent and as-expected, please specify a format.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        col_as_datetime: pd.Series = pd.to_datetime(col_data, errors='coerce')
    if col_as_datetime.isna().any():
        return OPTIMIZED_DTYPES['category']
    else:
        return OPTIMIZED_DTYPES['datetime']


def _optimized_numeric_dtypes(col_data: pd.Series) -> str:
    """
    Determines the optimized numeric data type for a given pandas Series
        by comparing the range of the column data with the ranges of each numeric data type.

    Spcial Note:
        Pandas does not support the float16 engine,
            and certain libraries may attempt to process your column as an index
            (for example, SDV, Gaussian Copula)
        Consequently, designating a column as float16 could lead to an error stating:
            "NotImplementedError: float16 indexes are not supported".
        As a result, we have chosen to set the minimum float type
            to float32 to avoid this issue.

    Args:
        col_data (pd.Series): The pandas Series containing the column data.

    Returns:
        str: The optimized numeric data type for the column.
    """
    ori_dtype: str = col_data.dtype.name
    opt_dtype: str = None

    # 1. verify if all of column belogn to np.nan
    if col_data.isna().all():
        return 'float32'
    
    # 2. Setting the ranges for each numeric data type
    if is_integer_dtype(col_data):
        RANGES = {
            'int8':  (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
            'int16': (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
            'int32': (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
            'int64': (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
        }
    elif is_float_dtype(col_data):
        RANGES = {
            'float32': (np.finfo(np.float32).min, np.finfo(np.float32).max),
            'float64': (np.finfo(np.float64).min, np.finfo(np.float64).max),
        }

    # 3. Check the range of the column data
    col_min, col_max = np.nanmin(col_data), np.nanmax(col_data)

    # 4. Infer the optimized dtype by their ranges
    for range_dtype, (min_val, max_val) in RANGES.items():
        if min_val <= col_min and col_max <= max_val:
            opt_dtype = range_dtype
            break

    # 5. If none of the ranges match,
    #    then return the original dtype define by pandas dtype.
    if opt_dtype is None:
        opt_dtype = ori_dtype

    return opt_dtype
