"""Pure functions for type inference operations"""

import re
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from petsard.metadater.types.data_types import DataType, LogicalType


def infer_pandas_dtype(series: pd.Series) -> str:
    """
    Pure function to infer pandas dtype from series

    Args:
        series: Pandas series to analyze

    Returns:
        String representation of pandas dtype
    """
    if isinstance(series.dtype, np.dtype):
        return series.dtype.name
    elif isinstance(series.dtype, pd.CategoricalDtype):
        return f"category[{series.dtype.categories.dtype.name}]"
    elif isinstance(series.dtype, pd.api.extensions.ExtensionDtype):
        return str(series.dtype)
    else:
        return str(series.dtype)


def map_pandas_to_metadater_type(pandas_dtype: str) -> DataType:
    """
    Pure function to convert pandas dtype to Metadater DataType

    Args:
        pandas_dtype: Pandas dtype string

    Returns:
        Corresponding DataType enum
    """
    dtype_str = pandas_dtype.lower()

    # Basic type mapping
    type_mapping = {
        "bool": DataType.BOOLEAN,
        "int8": DataType.INT8,
        "int16": DataType.INT16,
        "int32": DataType.INT32,
        "int64": DataType.INT64,
        "uint8": DataType.INT16,  # Promote unsigned to next larger signed
        "uint16": DataType.INT32,
        "uint32": DataType.INT64,
        "uint64": DataType.INT64,
        "float16": DataType.FLOAT32,
        "float32": DataType.FLOAT32,
        "float64": DataType.FLOAT64,
        "object": DataType.STRING,
        "string": DataType.STRING,
        "category": DataType.STRING,
    }

    # Handle datetime types
    if dtype_str.startswith("datetime64"):
        if "utc" in dtype_str.lower() or "tz" in dtype_str.lower():
            return DataType.TIMESTAMP_TZ
        return DataType.TIMESTAMP

    # Handle category types
    if dtype_str.startswith("category"):
        return DataType.STRING

    return type_mapping.get(dtype_str, DataType.STRING)


def detect_logical_type_patterns(
    series: pd.Series,
    sample_size: Optional[int] = 1000,
    confidence_threshold: float = 0.95,
) -> Optional[LogicalType]:
    """
    Pure function to detect logical type from data patterns

    Args:
        series: Pandas series to analyze
        sample_size: Maximum number of samples to analyze
        confidence_threshold: Minimum confidence required for detection

    Returns:
        Detected LogicalType or None
    """
    # Only analyze string-like data
    if not _is_string_compatible(series):
        return None

    sample = series.dropna()
    if len(sample) == 0:
        return None

    # Limit sample size for performance
    if sample_size and len(sample) > sample_size:
        sample = sample.sample(n=sample_size, random_state=42)

    # Ensure string operations are possible
    try:
        if not pd.api.types.is_string_dtype(sample):
            sample = sample.astype(str)
    except Exception:
        return None

    # Get pattern definitions
    patterns = _get_logical_type_patterns()

    # Check each pattern
    for logical_type, (pattern, threshold) in patterns.items():
        try:
            matches = sample.str.match(pattern, na=False)
            match_ratio = matches.sum() / len(matches) if len(matches) > 0 else 0.0

            if match_ratio >= max(threshold, confidence_threshold):
                # Special validation for certain types
                if logical_type in [
                    LogicalType.LATITUDE,
                    LogicalType.LONGITUDE,
                    LogicalType.PERCENTAGE,
                    LogicalType.CURRENCY,
                ]:
                    if not _validate_special_logical_type(
                        sample, logical_type, threshold
                    ):
                        continue
                return logical_type
        except Exception:
            continue

    # Check for categorical data (low cardinality)
    unique_ratio = series.nunique() / len(series)
    if unique_ratio < 0.05:  # 5% threshold
        return LogicalType.CATEGORICAL

    return None


def infer_optimal_dtype(
    series: pd.Series,
    current_dtype: Optional[str] = None,
    logical_type: Optional[LogicalType] = None,
) -> str:
    """
    Pure function to infer optimal dtype for storage

    Args:
        series: Pandas series to analyze
        current_dtype: Current dtype string
        logical_type: Detected logical type

    Returns:
        Optimal dtype string
    """
    # 首先檢查前導零情況
    if _has_leading_zeros_inference(series):
        return "string"

    # If logical type suggests category, use category
    if logical_type == LogicalType.CATEGORICAL:
        return "category"

    # For numeric data, find the smallest suitable type
    if is_numeric_dtype(series):
        return _optimize_numeric_dtype(series)

    # For object data, try to optimize
    elif is_object_dtype(series):
        return _optimize_object_dtype(series)

    # For other types, keep current
    return current_dtype or str(series.dtype)


def detect_datetime_format(series: pd.Series, sample_size: int = 100) -> Optional[str]:
    """
    Pure function to detect datetime format from string data

    Args:
        series: Series with potential datetime strings
        sample_size: Number of samples to analyze

    Returns:
        Detected datetime format string or None
    """
    if not _is_string_compatible(series):
        return None

    sample = series.dropna().head(sample_size)
    if len(sample) == 0:
        return None

    # Common datetime formats to try
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S.%f",
        "%m/%d/%Y",
        "%m-%d-%Y",
    ]

    for fmt in formats:
        try:
            # Try to parse a few samples
            parsed_count = 0
            for value in sample.head(10):
                try:
                    pd.to_datetime(str(value), format=fmt)
                    parsed_count += 1
                except Exception:
                    continue

            # If most samples parse successfully, this is likely the format
            if parsed_count >= len(sample.head(10)) * 0.8:
                return fmt
        except Exception:
            continue

    return None


def analyze_cardinality(series: pd.Series) -> Dict[str, Any]:
    """
    Pure function to analyze cardinality characteristics

    Args:
        series: Series to analyze

    Returns:
        Dictionary with cardinality analysis
    """
    total_count = len(series)
    unique_count = series.nunique()
    null_count = series.isna().sum()

    if total_count == 0:
        return {
            "total_count": 0,
            "unique_count": 0,
            "null_count": 0,
            "cardinality_ratio": 0.0,
            "is_unique": False,
            "is_low_cardinality": False,
            "is_high_cardinality": False,
        }

    cardinality_ratio = unique_count / total_count

    return {
        "total_count": int(total_count),
        "unique_count": int(unique_count),
        "null_count": int(null_count),
        "cardinality_ratio": round(cardinality_ratio, 4),
        "is_unique": cardinality_ratio >= 0.95,
        "is_low_cardinality": cardinality_ratio <= 0.05,
        "is_high_cardinality": cardinality_ratio >= 0.8,
    }


# Helper functions


def _is_string_compatible(series: pd.Series) -> bool:
    """Check if series can use string operations"""
    if pd.api.types.is_string_dtype(series):
        return True
    if pd.api.types.is_object_dtype(series):
        try:
            non_null = series.dropna()
            if len(non_null) == 0:
                return False
            return all(isinstance(x, str) for x in non_null.head(100))
        except Exception:
            return False
    return False


def _get_logical_type_patterns() -> Dict[LogicalType, Tuple[str, float]]:
    """Get logical type detection patterns with confidence thresholds"""
    return {
        LogicalType.EMAIL: (r"^[\w\.-]+@[\w\.-]+\.\w+$", 0.95),
        LogicalType.URL: (r"^https?://[^\s]+$", 0.95),
        LogicalType.IP_ADDRESS: (
            r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            0.95,
        ),
        LogicalType.UUID: (
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
            0.98,
        ),
        LogicalType.PHONE: (r"^[\+]?[\d\s\-\(\)]{10,}$", 0.90),
        LogicalType.POSTAL_CODE: (r"^[\d\w\s\-]{3,10}$", 0.85),
    }


def _validate_special_logical_type(
    sample: pd.Series, logical_type: LogicalType, threshold: float
) -> bool:
    """Validate special logical types with custom logic"""
    validators = {
        LogicalType.LATITUDE: _validate_latitude_values,
        LogicalType.LONGITUDE: _validate_longitude_values,
        LogicalType.PERCENTAGE: _validate_percentage_values,
        LogicalType.CURRENCY: _validate_currency_values,
    }

    validator = validators.get(logical_type)
    if not validator:
        return True

    try:
        valid_count = sum(validator(str(x)) for x in sample)
        return (valid_count / len(sample)) >= threshold
    except Exception:
        return False


def _validate_latitude_values(value: str) -> bool:
    """Validate latitude value"""
    try:
        lat = float(value)
        return -90 <= lat <= 90
    except (ValueError, TypeError):
        return False


def _validate_longitude_values(value: str) -> bool:
    """Validate longitude value"""
    try:
        lon = float(value)
        return -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def _validate_percentage_values(value: str) -> bool:
    """Validate percentage value"""
    if value.endswith("%"):
        try:
            float(value[:-1])
            return True
        except ValueError:
            return False
    try:
        num = float(value)
        return 0 <= num <= 1 or 0 <= num <= 100
    except ValueError:
        return False


def _validate_currency_values(value: str) -> bool:
    """Validate currency value"""
    currency_patterns = [
        r"^\$[\d,]+\.?\d*$",
        r"^[\d,]+\.?\d*\$$",
        r"^€[\d,]+\.?\d*$",
        r"^£[\d,]+\.?\d*$",
        r"^¥[\d,]+\.?\d*$",
        r"^[A-Z]{3}\s?[\d,]+\.?\d*$",
    ]
    return any(re.match(pattern, value) for pattern in currency_patterns)


def _is_float_with_integer_values_inference(series: pd.Series) -> bool:
    """
    檢測 float 序列是否實際上都是整數值（type_inference 版本）

    Args:
        series: 要檢查的 Series

    Returns:
        True 如果所有非空值都是整數，False 否則
    """
    if not is_float_dtype(series):
        return False

    # 移除空值
    clean_data = series.dropna()
    if len(clean_data) == 0:
        return False

    # 檢查所有值是否都是整數
    try:
        return all(val.is_integer() for val in clean_data)
    except (AttributeError, TypeError):
        return False


def _optimize_numeric_dtype(series: pd.Series) -> str:
    """Optimize numeric dtype to smallest suitable type"""
    if is_integer_dtype(series):
        # 如果有空值，使用 nullable integer 避免轉為 float
        if series.isna().any():
            if series.isna().all():
                return "Int64"

            col_min, col_max = np.nanmin(series), np.nanmax(series)

            # 使用 nullable integer types
            ranges = [
                ("Int8", np.iinfo(np.int8).min, np.iinfo(np.int8).max),
                ("Int16", np.iinfo(np.int16).min, np.iinfo(np.int16).max),
                ("Int32", np.iinfo(np.int32).min, np.iinfo(np.int32).max),
                ("Int64", np.iinfo(np.int64).min, np.iinfo(np.int64).max),
            ]

            for dtype, min_val, max_val in ranges:
                if min_val <= col_min and col_max <= max_val:
                    return dtype
            return "Int64"
        else:
            # 沒有空值時使用傳統 integer types
            col_min, col_max = np.nanmin(series), np.nanmax(series)

            ranges = [
                ("int8", np.iinfo(np.int8).min, np.iinfo(np.int8).max),
                ("int16", np.iinfo(np.int16).min, np.iinfo(np.int16).max),
                ("int32", np.iinfo(np.int32).min, np.iinfo(np.int32).max),
                ("int64", np.iinfo(np.int64).min, np.iinfo(np.int64).max),
            ]

            for dtype, min_val, max_val in ranges:
                if min_val <= col_min and col_max <= max_val:
                    return dtype
            return "int64"

    elif is_float_dtype(series):
        # 檢查是否實際上是整數值
        if _is_float_with_integer_values_inference(series):
            # 轉換為 nullable integer
            if series.isna().all():
                return "Int64"

            col_min, col_max = np.nanmin(series), np.nanmax(series)

            ranges = [
                ("Int8", np.iinfo(np.int8).min, np.iinfo(np.int8).max),
                ("Int16", np.iinfo(np.int16).min, np.iinfo(np.int16).max),
                ("Int32", np.iinfo(np.int32).min, np.iinfo(np.int32).max),
                ("Int64", np.iinfo(np.int64).min, np.iinfo(np.int64).max),
            ]

            for dtype, min_val, max_val in ranges:
                if min_val <= col_min and col_max <= max_val:
                    return dtype
            return "Int64"
        else:
            # 真正的浮點數
            if series.isna().all():
                return "float32"

            col_min, col_max = np.nanmin(series), np.nanmax(series)

            # Check if float32 is sufficient
            if (
                np.finfo(np.float32).min <= col_min
                and col_max <= np.finfo(np.float32).max
            ):
                return "float32"
            else:
                return "float64"

    return str(series.dtype)


def _has_leading_zeros_inference(series: pd.Series) -> bool:
    """
    檢測字串是否包含前導零的數字（type_inference 版本）

    Args:
        series: 要檢查的 Series

    Returns:
        True 如果發現前導零模式，False 否則
    """
    if series.isna().all():
        return False

    clean_series = series.dropna()
    if len(clean_series) == 0:
        return False

    # 轉換為字串進行檢查
    try:
        series_str = clean_series.astype(str)
    except Exception:
        return False

    # 檢查前導零模式：開頭是 "0" 且後面跟數字
    leading_zero_count = 0
    total_checked = 0

    for value in series_str.head(100):  # 檢查前100個值以提高效能
        value = value.strip()
        if len(value) >= 2:  # 至少要有兩個字符
            # 檢查是否符合前導零模式：0開頭且全部都是數字
            if value.startswith("0") and value.isdigit():
                leading_zero_count += 1
            total_checked += 1

    # 如果超過30%的值有前導零，則認為這是前導零欄位
    if total_checked > 0:
        return (leading_zero_count / total_checked) >= 0.3

    return False


def _optimize_object_dtype(series: pd.Series) -> str:
    """Optimize object dtype"""
    if series.isna().all():
        return "category"

    clean_series = series.dropna()

    # 首先檢查是否有前導零，如果有則保持為字串
    if _has_leading_zeros_inference(series):
        return "string"

    # Try datetime conversion
    try:
        datetime_series = pd.to_datetime(clean_series, errors="coerce")
        if not datetime_series.isna().any():
            return "datetime64[ns]"
    except Exception:
        pass

    # Default to category for object types
    return "category"
