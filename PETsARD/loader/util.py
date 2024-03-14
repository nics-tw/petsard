from dateutil.parser import parse
from typing import (
    Dict,
)
import warnings

import pandas as pd
from pandas.api.types import is_object_dtype

from PETsARD.error import ConfigError


ALLOWED_COLUMN_TYPES: dict = {
    'category': 'category',
    'date': 'datetime64[D]',
    'datetime': 'datetime64[s]',
}


def verify_column_types(column_types: Dict[str, list] = None) -> bool:
    """
    Verify the column types setting is valid or not.

    Args:
        column_types (dict):
            The dictionary of column names and their types.
            Format as {type: [colname]}
            Only below types are supported (case-insensitive):
            - 'category': The column will be treated as categorical.
            - 'date': The column will be treated as date.
            - 'datetime': The column will be treated as datetime.
    """
    return all(
        coltype.lower() in ALLOWED_COLUMN_TYPES.keys()
        for coltype in column_types.keys()
    )


def optimize_dtype(
    data: pd.DataFrame,
    column_types: Dict[str, list] = None
) -> Dict[str, str]:
    """
    Force setting discrete and datetime columns been load as str at first.

    Args:
        data (pd.DataFrame): The dataframe to be checked.
        column_types (dict): The column types to be forced assigned.

    Return:
        optimize_dtype (dict):
            dtype: particular columns been force assign as string
    """
    original_dtype = data.dtypes
    optimize_dtype: Dict[str, str] = {}

    # 1. if column_types is setting, force assign dtype
    if column_types is not None:
        if not verify_column_types(column_types):
            raise ConfigError
        for coltype in ALLOWED_COLUMN_TYPES.keys():
            if coltype in column_types:
                for colname in column_types[coltype]:
                    optimize_dtype[colname] = ALLOWED_COLUMN_TYPES[coltype]

    # 2. retrive remain columns not been assigned by column_types
    remain_col: list = list(
        set(original_dtype.keys()) - set(optimize_dtype.keys())
    )

    # 3. for remain columns
    for colname, dtype in original_dtype.items():
        if colname in remain_col:
            col_data: pd.Series = data[colname]
            col_data.dropna(inplace=True)
            # 3-1. if dtype is object, force assign as category
            if dtype == 'object':
                optimize_dtype[colname] = _optimized_object_dtype(
                    col_data=col_data
                )
                continue

    return optimize_dtype


def _optimized_object_dtype(col_data: pd.Series) -> str:
    """
    Determine the optimized column type for a given pandas Series of object dtype.

    Parameters:
        col_data (pd.Series): The pandas Series containing the column data.

    Returns:
        str: The optimized column type.

    Raises:
        TypeError: If the column data is not of object dtype.

    """
    if not is_object_dtype(col_data.dtype):
        raise TypeError

    # ignore below UserWarning from pandas
    #   UserWarning: Could not infer format,
    #       so each element will be parsed individually, falling back to `dateutil`.
    #       To ensure parsing is consistent and as-expected, please specify a format.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        col_as_datetime: pd.Series = pd.to_datetime(col_data, errors='coerce')
    if col_as_datetime.notna().any():
        if      (col_as_datetime.dt.hour   == 0).all() \
            and (col_as_datetime.dt.minute == 0).all() \
            and (col_as_datetime.dt.second == 0).all():
                return ALLOWED_COLUMN_TYPES['date']
        else:
            return ALLOWED_COLUMN_TYPES['datetime']
    else:
        return ALLOWED_COLUMN_TYPES['category']
