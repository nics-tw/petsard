"""Pure functions for field-level operations"""

import re
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from petsard.metadater.types.data_types import DataType, LogicalType
from petsard.metadater.types.field_types import FieldConfig, FieldMetadata, FieldStats


def build_field_metadata(
    field_data: pd.Series,
    field_name: str,
    config: Optional[FieldConfig] = None,
    compute_stats: bool = True,
    infer_logical_type: bool = True,
    optimize_dtype: bool = True,
    sample_size: Optional[int] = 1000,
) -> FieldMetadata:
    """
    Pure function to build FieldMetadata from a pandas Series

    Args:
        field_data: The pandas Series to analyze
        field_name: Name of the field
        config: Optional field configuration
        compute_stats: Whether to compute statistics
        infer_logical_type: Whether to infer logical type
        optimize_dtype: Whether to optimize dtype
        sample_size: Sample size for analysis

    Returns:
        FieldMetadata object
    """
    if config is None:
        config = FieldConfig()

    # Determine data type
    pandas_dtype = _safe_dtype_string(field_data.dtype)
    data_type = _map_pandas_to_metadater_type(pandas_dtype)

    # Override with type hint if provided
    if config.type_hint:
        data_type = _apply_type_hint(config.type_hint, data_type)

    # Determine nullable
    nullable = (
        config.nullable if config.nullable is not None else field_data.isna().any()
    )

    # Build base metadata
    field_metadata = FieldMetadata(
        name=field_name,
        data_type=data_type,
        nullable=nullable,
        source_dtype=pandas_dtype,
        description=config.description,
        cast_error=config.cast_error,
        properties=config.properties.copy(),
    )

    # Infer logical type
    if infer_logical_type:
        if config.logical_type:
            try:
                logical_type = LogicalType(config.logical_type)
                field_metadata = field_metadata.with_logical_type(logical_type)
            except ValueError:
                # Invalid logical type, infer from data
                logical_type = infer_field_logical_type(field_data, field_metadata)
                if logical_type:
                    field_metadata = field_metadata.with_logical_type(logical_type)
        else:
            logical_type = infer_field_logical_type(field_data, field_metadata)
            if logical_type:
                field_metadata = field_metadata.with_logical_type(logical_type)

    # Calculate statistics
    if compute_stats:
        sample_data = field_data
        if sample_size and len(field_data) > sample_size:
            sample_data = field_data.sample(n=sample_size, random_state=42)
        stats = calculate_field_stats(sample_data, field_metadata)
        field_metadata = field_metadata.with_stats(stats)

    # Determine optimal target dtype
    if optimize_dtype:
        target_dtype = optimize_field_dtype(field_data, field_metadata)
        field_metadata = field_metadata.with_target_dtype(target_dtype)

    return field_metadata


def calculate_field_stats(
    field_data: pd.Series, field_metadata: FieldMetadata
) -> FieldStats:
    """
    Pure function to calculate field statistics

    Args:
        field_data: The pandas Series to analyze
        field_metadata: Field metadata for context

    Returns:
        FieldStats object
    """
    stats = FieldStats(
        row_count=len(field_data),
        na_count=int(field_data.isna().sum()),
    )

    # Calculate na_percentage
    na_percentage = (
        (stats.na_count / stats.row_count) * 100 if stats.row_count > 0 else 0.0
    )
    stats = FieldStats(
        row_count=stats.row_count,
        na_count=stats.na_count,
        na_percentage=round(na_percentage, 4),
        distinct_count=int(field_data.nunique()),
    )

    # For numeric types, calculate additional stats
    if field_metadata.data_type in [
        DataType.INT8,
        DataType.INT16,
        DataType.INT32,
        DataType.INT64,
        DataType.FLOAT32,
        DataType.FLOAT64,
    ]:
        if not field_data.dropna().empty:
            quantiles = {
                0.25: field_data.quantile(0.25),
                0.5: field_data.quantile(0.5),
                0.75: field_data.quantile(0.75),
            }

            stats = FieldStats(
                row_count=stats.row_count,
                na_count=stats.na_count,
                na_percentage=stats.na_percentage,
                distinct_count=stats.distinct_count,
                min_value=field_data.min(),
                max_value=field_data.max(),
                mean_value=float(field_data.mean()),
                std_value=float(field_data.std()),
                quantiles=quantiles,
            )

    # Most frequent values
    value_counts = field_data.value_counts().head(10)
    if not value_counts.empty:
        most_frequent = list(zip(value_counts.index, value_counts.values))
        stats = FieldStats(
            row_count=stats.row_count,
            na_count=stats.na_count,
            na_percentage=stats.na_percentage,
            distinct_count=stats.distinct_count,
            min_value=stats.min_value,
            max_value=stats.max_value,
            mean_value=stats.mean_value,
            std_value=stats.std_value,
            quantiles=stats.quantiles,
            most_frequent=most_frequent,
        )

    return stats


def infer_field_logical_type(
    field_data: pd.Series, field_metadata: FieldMetadata
) -> Optional[LogicalType]:
    """
    Pure function to infer logical type from data patterns

    Args:
        field_data: The pandas Series to analyze
        field_metadata: Field metadata for context

    Returns:
        Inferred LogicalType or None
    """
    # Only process string-like data
    if field_metadata.data_type not in [DataType.STRING, DataType.BINARY]:
        return None

    sample = field_data.dropna()
    if len(sample) == 0:
        return None

    # Limit sample size
    if len(sample) > 1000:
        sample = sample.sample(n=1000, random_state=42)

    # Ensure string operations are possible
    if not _is_string_compatible(sample):
        return None

    try:
        if not pd.api.types.is_string_dtype(sample):
            sample = sample.astype(str)
    except Exception:
        return None

    # Check patterns
    patterns = _get_logical_type_patterns()
    for logical_type, (pattern, threshold) in patterns.items():
        try:
            matches = sample.str.match(pattern, na=False)
            match_ratio = matches.sum() / len(matches)

            if match_ratio >= threshold:
                # Special validation for certain types
                if logical_type in [
                    LogicalType.LATITUDE,
                    LogicalType.LONGITUDE,
                    LogicalType.PERCENTAGE,
                    LogicalType.CURRENCY,
                ]:
                    validator = _get_special_validator(logical_type)
                    if not _validate_with_function(sample, validator, threshold):
                        continue
                return logical_type
        except Exception:
            continue

    # Check categorical
    unique_ratio = field_data.nunique() / len(field_data)
    if unique_ratio < 0.05:  # 5% threshold
        return LogicalType.CATEGORICAL

    return None


def optimize_field_dtype(field_data: pd.Series, field_metadata: FieldMetadata) -> str:
    """
    Pure function to determine optimal dtype for storage

    Args:
        field_data: The pandas Series to analyze
        field_metadata: Field metadata for context

    Returns:
        Optimal dtype string
    """
    if (
        field_metadata.data_type == DataType.STRING
        and field_metadata.logical_type == LogicalType.CATEGORICAL
    ):
        return "category"

    if is_numeric_dtype(field_data):
        return _optimize_numeric_dtype(field_data)
    elif is_object_dtype(field_data):
        return _optimize_object_dtype(field_data)

    return str(field_data.dtype)


# Helper functions (pure)


def _safe_dtype_string(dtype: Any) -> str:
    """Convert various dtype representations to string"""
    if isinstance(dtype, np.dtype):
        return dtype.name
    elif isinstance(dtype, pd.CategoricalDtype):
        return f"category[{dtype.categories.dtype.name}]"
    elif isinstance(dtype, pd.api.extensions.ExtensionDtype):
        return str(dtype)
    elif isinstance(dtype, str):
        return dtype
    elif isinstance(dtype, type):
        return dtype.__name__.lower()
    else:
        return str(dtype)


def _map_pandas_to_metadater_type(pandas_dtype: str) -> DataType:
    """Convert pandas dtype to Metadater DataType"""
    dtype_str = pandas_dtype.lower()

    mapping = {
        "bool": DataType.BOOLEAN,
        "int8": DataType.INT8,
        "int16": DataType.INT16,
        "int32": DataType.INT32,
        "int64": DataType.INT64,
        "uint8": DataType.INT16,
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

    if dtype_str.startswith("datetime64"):
        if "utc" in dtype_str.lower() or "tz" in dtype_str.lower():
            return DataType.TIMESTAMP_TZ
        return DataType.TIMESTAMP

    if dtype_str.startswith("category"):
        return DataType.STRING

    return mapping.get(dtype_str, DataType.STRING)


def _apply_type_hint(type_hint: str, current_type: DataType) -> DataType:
    """Apply type hint to determine data type"""
    type_hint = type_hint.lower()
    type_mapping = {
        "category": DataType.STRING,
        "datetime": DataType.TIMESTAMP,
        "date": DataType.DATE,
        "time": DataType.TIME,
        "int": DataType.INT64,
        "integer": DataType.INT64,
        "float": DataType.FLOAT64,
        "string": DataType.STRING,
        "boolean": DataType.BOOLEAN,
    }
    return type_mapping.get(type_hint, current_type)


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
    }


def _get_special_validator(logical_type: LogicalType) -> Callable[[str], bool]:
    """Get special validator function for logical type"""
    validators = {
        LogicalType.LATITUDE: _validate_latitude,
        LogicalType.LONGITUDE: _validate_longitude,
        LogicalType.PERCENTAGE: _validate_percentage,
        LogicalType.CURRENCY: _validate_currency,
    }
    return validators[logical_type]


def _validate_with_function(
    sample: pd.Series, validator: Callable[[str], bool], threshold: float
) -> bool:
    """Validate sample using a custom validator function"""
    try:
        valid_count = sum(validator(x) for x in sample)
        return (valid_count / len(sample)) >= threshold
    except Exception:
        return False


def _validate_latitude(value: str) -> bool:
    """Validate latitude"""
    try:
        lat = float(value)
        return -90 <= lat <= 90
    except (ValueError, TypeError):
        return False


def _validate_longitude(value: str) -> bool:
    """Validate longitude"""
    try:
        lon = float(value)
        return -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def _validate_percentage(value: str) -> bool:
    """Validate percentage"""
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


def _validate_currency(value: str) -> bool:
    """Validate currency"""
    currency_patterns = [
        r"^\$[\d,]+\.?\d*$",
        r"^[\d,]+\.?\d*\$$",
        r"^€[\d,]+\.?\d*$",
        r"^£[\d,]+\.?\d*$",
        r"^¥[\d,]+\.?\d*$",
        r"^[A-Z]{3}\s?[\d,]+\.?\d*$",
    ]
    return any(re.match(pattern, value) for pattern in currency_patterns)


def _optimize_numeric_dtype(field_data: pd.Series) -> str:
    """Optimize numeric dtype"""
    if is_integer_dtype(field_data):
        if field_data.isna().all():
            return "int64"

        ranges = {
            "int8": (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
            "int16": (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
            "int32": (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
            "int64": (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
        }
    elif is_float_dtype(field_data):
        if field_data.isna().all():
            return "float32"

        ranges = {
            "float32": (np.finfo(np.float32).min, np.finfo(np.float32).max),
            "float64": (np.finfo(np.float64).min, np.finfo(np.float64).max),
        }
    else:
        return str(field_data.dtype)

    col_min, col_max = np.nanmin(field_data), np.nanmax(field_data)

    for dtype, (min_val, max_val) in ranges.items():
        if min_val <= col_min and col_max <= max_val:
            return dtype

    return str(field_data.dtype)


def _optimize_object_dtype(field_data: pd.Series) -> str:
    """Optimize object dtype"""
    if field_data.isna().all():
        return "category"

    field_data_clean = field_data.dropna()

    # Try datetime conversion
    try:
        datetime_field_data = pd.to_datetime(field_data_clean, errors="coerce")
        if not datetime_field_data.isna().any():
            return "datetime64[s]"
    except Exception:
        pass

    return "category"
