import logging
import warnings
from typing import Dict, Union

import numpy as np
import pandas as pd
from numpy.core._dtype import _kind_name
from pandas.api.types import (
    is_bool_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from petsard.exceptions import ConfigError
from petsard.util.params import ALLOWED_COLUMN_TYPES, OPTIMIZED_DTYPES

# 常數定義
NUMERIC_MAP: dict[str, int] = {
    "int8": 8,
    "int16": 16,
    "int32": 32,
    "int64": 64,
    "float32": 32,
    "float64": 64,
}


# 型別處理核心函數
def safe_dtype(
    dtype: Union[
        str,
        type,
        np.dtype,
        pd.CategoricalDtype,
        pd.IntervalDtype,
        pd.PeriodDtype,
        pd.SparseDtype,
    ],
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

    dtype_name: str = ""

    if isinstance(dtype, np.dtype):
        dtype_name = dtype.name
    elif isinstance(dtype, pd.CategoricalDtype):
        dtype_name = f"category[{_kind_name(dtype.categories.dtype)}]"
    elif isinstance(dtype, pd.IntervalDtype):
        dtype_name = f"interval[{dtype.subtype}]"
    elif isinstance(dtype, pd.PeriodDtype):
        dtype_name = dtype.name
    elif isinstance(dtype, pd.SparseDtype):
        dtype_name = dtype.name
    elif isinstance(dtype, str):
        dtype_name = dtype
    elif isinstance(dtype, type):
        dtype_name = dtype.__name__.lower()
        if not (
            dtype_name == "str"
            or dtype_name.startswith("int")
            or dtype_name.startswith("float")
        ):
            raise TypeError(f"Unsupported data type: {dtype_name}")
    else:
        raise TypeError(f"Unsupported data type: {dtype}")

    return dtype_name.lower()


def safe_infer_dtype(safe_dtype: str) -> str:
    """
    Auxiliary function for inferring dtypes.
        Please using safe_dtype() before calling this function.

    Args:
        safe_dtype (str): The data type from the data.

    Return:
        (str): The inferred data type.

    Raises:
        TypeError: If the input data type is not supported.
    """
    if safe_dtype is None:
        raise TypeError(f"{safe_dtype} is invalid.")

    if pd.api.types.is_bool_dtype(safe_dtype):
        return "categorical"
    elif pd.api.types.is_numeric_dtype(safe_dtype):
        return "numerical"
    elif safe_dtype == "category":
        return "categorical"
    elif pd.api.types.is_datetime64_any_dtype(safe_dtype):
        return "datetime"
    elif pd.api.types.is_object_dtype(safe_dtype):
        return "object"
    else:
        raise TypeError(f"{safe_dtype} is invalid.")


# 優化相關函數
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
    if col_data.isna().all():
        return OPTIMIZED_DTYPES["category"]

    col_data.dropna(inplace=True)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        col_as_datetime: pd.Series = pd.to_datetime(col_data, errors="coerce")
    if col_as_datetime.isna().any():
        return OPTIMIZED_DTYPES["category"]
    else:
        return OPTIMIZED_DTYPES["datetime"]


def _optimized_numeric_dtypes(col_data: pd.Series) -> str:
    """
    Determines the optimized numeric data type for a given pandas Series
        by comparing the range of the column data with the ranges of each numeric data type.

    Args:
        col_data (pd.Series): The pandas Series containing the column data.

    Returns:
        str: The optimized numeric data type for the column.
    """
    ori_dtype: str = col_data.dtype.name
    opt_dtype: str = None

    if col_data.isna().all():
        return "float32"

    if is_integer_dtype(col_data):
        RANGES = {
            "int8": (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
            "int16": (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
            "int32": (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
            "int64": (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
        }
    elif is_float_dtype(col_data):
        RANGES = {
            "float32": (np.finfo(np.float32).min, np.finfo(np.float32).max),
            "float64": (np.finfo(np.float64).min, np.finfo(np.float64).max),
        }

    col_min, col_max = np.nanmin(col_data), np.nanmax(col_data)

    for range_dtype, (min_val, max_val) in RANGES.items():
        if min_val <= col_min and col_max <= max_val:
            opt_dtype = range_dtype
            break

    if opt_dtype is None:
        opt_dtype = ori_dtype

    return opt_dtype


def optimize_dtype(col_data: pd.Series) -> str:
    """
    Optimize the data type of a single column.

    Args:
        col_data (pd.Series): The column data to be optimized.

    Returns:
        str: The optimized data type for the column.
    """
    opt_dtype: str = ""
    if is_object_dtype(col_data):
        opt_dtype = _optimized_object_dtypes(col_data=col_data)
    elif is_bool_dtype(col_data):
        opt_dtype = col_data.dtype.name
    elif is_numeric_dtype(col_data):
        opt_dtype = _optimized_numeric_dtypes(col_data=col_data)
    else:
        opt_dtype = col_data.dtype.name
    return opt_dtype


def optimize_dtypes(
    data: pd.DataFrame, column_types: Dict[str, list] = None
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

    if column_types is not None:
        if not verify_column_types(column_types):
            raise ConfigError
        for coltype in ALLOWED_COLUMN_TYPES:
            if coltype in column_types:
                for colname in column_types[coltype]:
                    optimize_dtypes[colname] = OPTIMIZED_DTYPES[coltype]

    remain_col: list = list(set(original_dtypes.keys()) - set(optimize_dtypes.keys()))

    for colname in remain_col:
        col_data: pd.Series = data[colname]
        optimize_dtypes[colname] = optimize_dtype(col_data)

    return optimize_dtypes


# 型別轉換函數
def safe_astype(
    col: pd.Series,
    declared_dtype: Union[
        str,
        type,
        np.dtype,
        pd.CategoricalDtype,
        pd.IntervalDtype,
        pd.PeriodDtype,
        pd.SparseDtype,
    ],
) -> pd.Series:
    """
    Safely cast a pandas Series to a given dtype.
    """
    logger = logging.getLogger(f"PETsARD.{__name__}")

    data_dtype_name: str = safe_dtype(col.dtype)
    declared_dtype_name: str = safe_dtype(declared_dtype)

    colname: str = "unknown"
    if col.name is not None:
        colname = col.name

    if data_dtype_name == "float16":
        logger.info(
            f"dtype {data_dtype_name} change to float32 first"
            + "for pandas only support float32 above.",
        )
        col = col.astype("float32")

    is_change_dtype: bool = False
    opt_dtype_name: str = ""
    is_type_error: bool = False
    is_value_error: bool = False
    declared_cardinality: list = None
    declared_cat_dtypes: set = None

    if is_integer_dtype(declared_dtype_name):
        if is_integer_dtype(data_dtype_name):
            opt_dtype_name = optimize_dtype(col)
            if NUMERIC_MAP[opt_dtype_name] < NUMERIC_MAP[declared_dtype_name]:
                is_change_dtype = True
            elif NUMERIC_MAP[opt_dtype_name] > NUMERIC_MAP[declared_dtype_name]:
                is_value_error = True
        elif is_float_dtype(data_dtype_name):
            col = col.round()
            is_change_dtype = True
        else:
            is_type_error = True
    elif is_float_dtype(declared_dtype_name):
        if declared_dtype_name == "float16" and (
            is_integer_dtype(data_dtype_name) or is_float_dtype(data_dtype_name)
        ):
            logger.info(
                f"declared dtype {declared_dtype_name} "
                + "will changes to float32 "
                + "for pandas only support float32 above.",
            )
            declared_dtype_name == "float32"
            is_change_dtype = True
        elif is_integer_dtype(data_dtype_name):
            is_change_dtype = True
        elif is_float_dtype(data_dtype_name):
            opt_dtype_name = optimize_dtype(col)
            if NUMERIC_MAP[opt_dtype_name] < NUMERIC_MAP[declared_dtype_name]:
                is_change_dtype = True
            elif NUMERIC_MAP[opt_dtype_name] > NUMERIC_MAP[declared_dtype_name]:
                is_value_error = True
        else:
            is_type_error = True
    elif declared_dtype_name.startswith("category"):
        is_change_dtype = True

        col_cardinality: list = col.unique().tolist()
        declared_cardinality: list = declared_dtype.categories.values.tolist()
        for cat_dtype in ["str", "float", "int"]:
            if all(item in declared_cardinality for item in col_cardinality):
                break

            declared_cat_dtypes = list(
                set(safe_dtype(type(item)) for item in declared_cardinality)
            )

            if cat_dtype in declared_cat_dtypes:
                if cat_dtype == "int":
                    col = col.round().astype(cat_dtype)
                else:
                    col = col.astype(cat_dtype)
                col_cardinality = col.unique().tolist()
    elif declared_dtype_name.startswith("datetime") and (
        is_float_dtype(data_dtype_name) or is_integer_dtype(data_dtype_name)
    ):
        is_change_dtype = True
    elif declared_dtype_name == "object":
        is_change_dtype = True
    elif is_bool_dtype(declared_dtype_name) and data_dtype_name == "category[bool]":
        is_change_dtype = True
    else:
        if data_dtype_name != declared_dtype_name:
            is_type_error = True

    if is_type_error:
        raise TypeError(
            f"The data type of {colname} is {data_dtype_name}, "
            + f"which is not aligned with the metadata: {declared_dtype_name}."
        )

    if is_value_error:
        raise ValueError(
            f"The data type of {colname} is {data_dtype_name}, "
            + f"and the optimized data type is {opt_dtype_name}, "
            + f"which is out of the range of the metadata: {declared_dtype_name}."
        )

    if is_change_dtype:
        if declared_dtype_name.startswith("category"):
            col = col.astype("category")
        else:
            col = col.astype(declared_dtype_name)

        logger.info(
            f"{colname} changes data dtype from "
            + f"{data_dtype_name} to {declared_dtype_name} "
            + "for metadata alignment.",
        )

    return col


def verify_column_types(column_types: Dict[str, list] = None) -> bool:
    """
    Verify the column types setting is valid or not.

    Args:
        column_types (dict):
            The dictionary of column names and their types.
            Format as {type: [colname]}
            Only below types are supported (case-insensitive):
            - 'category': The column will be treated as categorical.
            - 'datetime': The column will be treated as datetime.
    """
    return all(
        coltype.lower() in ALLOWED_COLUMN_TYPES for coltype in column_types.keys()
    )


def align_dtypes(
    data: pd.DataFrame,
    metadata,
) -> pd.DataFrame:
    """
    Align the data types between the metadata from ori data
        and the data to be aligned.

    metadata should be Metadata object,
        but we don't set a type hint
        for don't import it here to avoid circular import.

    Args:
        data (pd.DataFrame): The data to be aligned.
        metadata (Metadata): The metadata of ori data.

    Return:
        (pd.DataFrame): The aligned data.
    """
    for col, val in metadata.metadata["col"].items():
        data[col] = safe_astype(data[col], val["dtype"])

    return data
