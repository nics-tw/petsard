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

from petsard.metadater.field.field_types import FieldConfig, FieldMetadata, FieldStats
from petsard.metadater.types.data_types import DataType, LogicalType


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

    # 檢查前導零情況，如果發現前導零則強制設為字串類型
    if config.auto_detect_leading_zeros:
        if (
            data_type in [DataType.INT8, DataType.INT16, DataType.INT32, DataType.INT64]
            or pandas_dtype == "object"
        ):
            if _has_leading_zeros(field_data):
                data_type = DataType.STRING

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
        target_dtype = optimize_field_dtype(field_data, field_metadata, config)
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


def optimize_field_dtype(
    field_data: pd.Series,
    field_metadata: FieldMetadata,
    config: Optional[FieldConfig] = None,
) -> str:
    """
    Pure function to determine optimal dtype for storage

    Args:
        field_data: The pandas Series to analyze
        field_metadata: Field metadata for context
        config: Optional field configuration

    Returns:
        Optimal dtype string
    """
    if config is None:
        config = FieldConfig()

    if (
        field_metadata.data_type == DataType.STRING
        and field_metadata.logical_type == LogicalType.CATEGORICAL
    ):
        return "category"

    # 使用完整的類型分析邏輯
    return _comprehensive_type_analysis(field_data, config)


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


def _is_float_with_integer_values(field_data: pd.Series) -> bool:
    """
    檢測 float 序列是否實際上都是整數值

    Args:
        field_data: 要檢查的 Series

    Returns:
        True 如果所有非空值都是整數，False 否則
    """
    if not is_float_dtype(field_data):
        return False

    # 移除空值
    clean_data = field_data.dropna()
    if len(clean_data) == 0:
        return False

    # 檢查所有值是否都是整數
    try:
        return all(val.is_integer() for val in clean_data)
    except (AttributeError, TypeError):
        return False


def _comprehensive_type_analysis(
    field_data: pd.Series, config: Optional[FieldConfig] = None
) -> str:
    """
    完整的類型分析邏輯，按照以下順序：
    1. 檢查前導零 -> 字串
    2. 檢查小數點 -> float
    3. 檢查整數（含空值處理）-> int/Int64
    4. 其他 -> category/string

    Args:
        field_data: 要分析的 Series
        config: 欄位配置

    Returns:
        最佳的 dtype 字串
    """
    if config is None:
        config = FieldConfig()

    # 1. 首先檢查前導零（無論原始類型為何）
    if config.auto_detect_leading_zeros and _has_leading_zeros(field_data):
        return "string"

    # 2. 統一嘗試數值轉換（無論原始類型為何）
    try:
        # 嘗試轉換為數值（保留 NaN）
        numeric_data = pd.to_numeric(field_data, errors="coerce")

        # 計算有效數值的比例
        non_na_count = field_data.notna().sum()
        valid_numeric_count = numeric_data.notna().sum()

        if non_na_count > 0 and valid_numeric_count > 0:
            valid_numeric_ratio = valid_numeric_count / non_na_count

            if valid_numeric_ratio >= 0.8:  # 80% 以上可以轉為數值
                valid_numeric_values = numeric_data.dropna()

                if len(valid_numeric_values) > 0:
                    # 檢查是否都是整數值
                    # 需要處理 int 和 float 兩種情況
                    try:
                        if is_integer_dtype(valid_numeric_values):
                            # 如果已經是整數類型，直接認為是整數
                            all_integers = True
                        else:
                            # 如果是浮點類型，檢查是否都是整數值
                            all_integers = all(
                                val.is_integer() for val in valid_numeric_values
                            )
                    except (AttributeError, TypeError):
                        # 如果無法判斷，假設不是整數
                        all_integers = False

                    if all_integers:
                        # 整數資料，檢查是否有空值
                        if field_data.isna().any() and config.force_nullable_integers:
                            return _optimize_nullable_integer_dtype(
                                valid_numeric_values
                            )
                        else:
                            return _optimize_regular_integer_dtype(valid_numeric_values)
                    else:
                        # 浮點數資料
                        return _optimize_float_dtype(numeric_data)

    except Exception:
        pass

    # 如果數值轉換失敗，但原本就是數值類型，使用原來的邏輯
    if is_numeric_dtype(field_data):
        return _optimize_numeric_dtype(field_data, config)

    # 3. 如果不是數值資料，檢查其他類型
    if is_object_dtype(field_data):
        # 對於 object 類型，先檢查是否為 datetime，否則返回 category
        clean_data = field_data.dropna()
        if len(clean_data) == 0:
            return "category"

        # 檢查是否為 datetime
        if _might_be_datetime(clean_data):
            try:
                datetime_data = pd.to_datetime(clean_data, errors="coerce")
                if not datetime_data.isna().any():
                    return "datetime64[s]"
            except Exception:
                pass

        return "category"
    elif is_numeric_dtype(field_data):
        # 如果原本就是數值類型，使用原來的邏輯
        return _optimize_numeric_dtype(field_data, config)

    # 其他情況保持原樣
    return str(field_data.dtype)


def _optimize_float_dtype(numeric_data: pd.Series) -> str:
    """優化浮點數類型"""
    if numeric_data.isna().all():
        return "float32"

    col_min, col_max = np.nanmin(numeric_data), np.nanmax(numeric_data)

    # 檢查是否 float32 足夠
    if np.finfo(np.float32).min <= col_min and col_max <= np.finfo(np.float32).max:
        return "float32"
    else:
        return "float64"


def _optimize_nullable_integer_dtype(integer_data: pd.Series) -> str:
    """優化 nullable integer 類型"""
    if len(integer_data) == 0:
        return "Int64"

    col_min, col_max = integer_data.min(), integer_data.max()

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


def _optimize_regular_integer_dtype(integer_data: pd.Series) -> str:
    """優化一般 integer 類型"""
    if len(integer_data) == 0:
        return "int64"

    col_min, col_max = integer_data.min(), integer_data.max()

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


def _optimize_numeric_dtype(
    field_data: pd.Series, config: Optional[FieldConfig] = None
) -> str:
    """Optimize numeric dtype"""
    if config is None:
        config = FieldConfig()

    if is_integer_dtype(field_data):
        # 如果有空值且啟用 force_nullable_integers，使用 nullable integer 避免轉為 float
        if field_data.isna().any() and config.force_nullable_integers:
            if field_data.isna().all():
                return "Int64"

            col_min, col_max = np.nanmin(field_data), np.nanmax(field_data)

            # 使用 nullable integer types
            ranges = {
                "Int8": (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
                "Int16": (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
                "Int32": (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
                "Int64": (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
            }

            for dtype, (min_val, max_val) in ranges.items():
                if min_val <= col_min and col_max <= max_val:
                    return dtype
            return "Int64"
        else:
            # 沒有空值時使用傳統 integer types
            col_min, col_max = np.nanmin(field_data), np.nanmax(field_data)

            ranges = {
                "int8": (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
                "int16": (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
                "int32": (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
                "int64": (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
            }

            for dtype, (min_val, max_val) in ranges.items():
                if min_val <= col_min and col_max <= max_val:
                    return dtype
            return "int64"

    elif is_float_dtype(field_data):
        # 檢查是否實際上是整數值
        if _is_float_with_integer_values(field_data):
            # 轉換為 nullable integer
            if field_data.isna().all():
                return "Int64"

            col_min, col_max = np.nanmin(field_data), np.nanmax(field_data)

            ranges = {
                "Int8": (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
                "Int16": (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
                "Int32": (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
                "Int64": (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
            }

            for dtype, (min_val, max_val) in ranges.items():
                if min_val <= col_min and col_max <= max_val:
                    return dtype
            return "Int64"
        else:
            # 真正的浮點數
            if field_data.isna().all():
                return "float32"

            col_min, col_max = np.nanmin(field_data), np.nanmax(field_data)

            ranges = {
                "float32": (np.finfo(np.float32).min, np.finfo(np.float32).max),
                "float64": (np.finfo(np.float64).min, np.finfo(np.float64).max),
            }

            for dtype, (min_val, max_val) in ranges.items():
                if min_val <= col_min and col_max <= max_val:
                    return dtype
            return "float64"
    else:
        return str(field_data.dtype)


def _might_be_datetime(field_data: pd.Series) -> bool:
    """
    Pre-check if field data might contain datetime values to avoid unnecessary parsing warnings.

    Args:
        field_data: Clean pandas Series (no NaN values)

    Returns:
        True if data might be datetime, False otherwise
    """
    if len(field_data) == 0:
        return False

    # Sample a few values to check
    sample_size = min(10, len(field_data))
    sample = field_data.head(sample_size)

    # Convert to string for pattern checking
    try:
        sample_str = sample.astype(str)
    except Exception:
        return False

    datetime_indicators = 0

    # First, check for obvious non-datetime patterns that should be excluded
    non_datetime_patterns = [
        "hs-grad",
        "some-college",
        "bachelors",
        "masters",
        "doctorate",
        "prof-school",
        "assoc-acdm",
        "assoc-voc",
        "11th",
        "10th",
        "9th",
        "7th-8th",
        "5th-6th",
        "machine-op-inspct",
        "farming-fishing",
        "protective-serv",
        "other-service",
        "never-married",
        "married-civ-spouse",
        "divorced",
        "separated",
        "widowed",
        "own-child",
        "husband",
        "wife",
        "not-in-family",
        "unmarried",
        "united-states",
        "asian-pac-islander",
        "amer-indian-eskimo",
    ]

    # Check if any sample values match common non-datetime patterns
    for value in sample_str:
        value_lower = value.strip().lower()
        if any(pattern in value_lower for pattern in non_datetime_patterns):
            return False  # Definitely not datetime data

    for value in sample_str:
        value = value.strip()

        # Skip very short strings (likely not datetime)
        if len(value) < 4:
            continue

        # Check for common datetime patterns
        # Date separators: -, /, .
        if any(sep in value for sep in ["-", "/", "."]):
            # Check if contains digits (years, months, days)
            if any(char.isdigit() for char in value):
                # Additional check: must have at least 4 consecutive digits (likely a year)
                # or multiple digit groups separated by separators
                import re

                digit_groups = re.findall(r"\d+", value)
                if len(digit_groups) >= 2 or any(
                    len(group) >= 4 for group in digit_groups
                ):
                    datetime_indicators += 1
                    continue

        # Check for time patterns (contains :)
        if ":" in value and any(char.isdigit() for char in value):
            datetime_indicators += 1
            continue

        # Check for month names
        month_names = [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
        if any(month in value.lower() for month in month_names):
            datetime_indicators += 1
            continue

    # Require at least 70% of sampled values to have strong datetime indicators
    # and ensure we actually checked some values
    if sample_size == 0:
        return False
    return datetime_indicators / sample_size >= 0.7


def _has_leading_zeros(field_data: pd.Series) -> bool:
    """
    檢測字串是否包含前導零的數字

    Args:
        field_data: 要檢查的 Series

    Returns:
        True 如果發現前導零模式，False 否則
    """
    if field_data.isna().all():
        return False

    field_data_clean = field_data.dropna()
    if len(field_data_clean) == 0:
        return False

    # 轉換為字串進行檢查
    try:
        field_data_str = field_data_clean.astype(str)
    except Exception:
        return False

    # 檢查前導零模式：開頭是 "0" 且後面跟數字
    leading_zero_count = 0
    total_checked = 0

    for value in field_data_str.head(100):  # 檢查前100個值以提高效能
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


def _optimize_object_dtype(
    field_data: pd.Series, config: Optional[FieldConfig] = None
) -> str:
    """Optimize object dtype"""
    if config is None:
        config = FieldConfig()

    if field_data.isna().all():
        return "category"

    field_data_clean = field_data.dropna()

    # 首先檢查是否有前導零，如果有則保持為字串
    if config.auto_detect_leading_zeros and _has_leading_zeros(field_data):
        return "string"

    # Pre-check if data might be datetime before attempting conversion
    # This avoids unnecessary datetime parsing warnings for obviously non-datetime data
    if _might_be_datetime(field_data_clean):
        # Try datetime conversion
        try:
            datetime_field_data = pd.to_datetime(field_data_clean, errors="coerce")
            if not datetime_field_data.isna().any():
                return "datetime64[s]"
        except Exception:
            pass

    return "category"
