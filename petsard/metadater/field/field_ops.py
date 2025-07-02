"""Field-level operations and transformations"""

import logging
import re
import warnings
from typing import Any, Callable, Optional, Union

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from petsard.metadater.datatype import DataType, LogicalType
from petsard.metadater.field.field_types import FieldConfig, FieldMetadata, FieldStats


class TypeMapper:
    """Maps between different type systems"""

    # Pandas to internal type mapping
    PANDAS_TO_METADATER = {
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
        "datetime64[ns]": DataType.TIMESTAMP,
        "datetime64[ns, UTC]": DataType.TIMESTAMP_TZ,
    }

    @staticmethod
    def _safe_dtype(dtype: Any) -> str:
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

    @classmethod
    def _pandas_to_metadater(cls, pandas_dtype: str) -> DataType:
        """Convert pandas dtype to Metadater DataType"""
        dtype_str = cls._safe_dtype(pandas_dtype).lower()

        if dtype_str.startswith("datetime64"):
            if "utc" in dtype_str.lower() or "tz" in dtype_str.lower():
                return DataType.TIMESTAMP_TZ
            return DataType.TIMESTAMP

        if dtype_str.startswith("category"):
            return DataType.STRING

        return cls.PANDAS_TO_METADATER.get(dtype_str, DataType.STRING)


class FieldOperations:
    """Operations for field-level metadata and transformations"""

    LOGICAL_CATEGORICAL_TYPE_PERCENTAGE: float = 0.05

    # Logical type detection patterns with confidence thresholds
    LOGICAL_TYPE_PATTERNS: dict[LogicalType, tuple[str, float]] = {
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
        # ... 其他 patterns
    }

    def __init__(self):
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self.SPECIAL_VALIDATORS = {
            LogicalType.LATITUDE: self._validate_latitude,
            LogicalType.LONGITUDE: self._validate_longitude,
            LogicalType.PERCENTAGE: self._validate_percentage,
            LogicalType.CURRENCY: self._validate_currency,
        }

    @classmethod
    def build_field_from_series(
        cls,
        field_data: pd.Series,
        field_name: str = "Unnamed Field",
        config: Optional[Union[FieldConfig, dict[str, Any]]] = None,
        compute_stats: bool = True,
        infer_logical_type: bool = True,
        optimize_dtype: bool = True,
        sample_size: Optional[int] = 1000,
    ) -> FieldMetadata:
        """Build FieldMetadata from a pandas Series"""
        if field_name == "Unnamed Field" and hasattr(field_data, "name"):
            field_name = str(field_data.name)

        instance = cls()
        instance._logger.debug(
            f"Building field metadata for '{field_name}' with length {len(field_data)}"
        )

        # Convert dict to FieldConfig if needed
        if config is not None and not isinstance(config, FieldConfig):
            if isinstance(config, dict):
                config = FieldConfig(**config)
            else:
                raise TypeError(
                    f"config must be FieldConfig or dict, got {type(config)}"
                )

        if config is None:
            config = FieldConfig()

        # Determine data type
        pandas_dtype: Any = TypeMapper._safe_dtype(field_data.dtype)
        data_type: DataType = TypeMapper._pandas_to_metadater(pandas_dtype)

        # Override with type hint if provided
        if config.type_hint:
            data_type = instance._apply_type_hint(config.type_hint, data_type)

        # Determine nullable
        nullable = (
            config.nullable if config.nullable is not None else field_data.isna().any()
        )

        # Build field metadata
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
                    field_metadata.logical_type = LogicalType(config.logical_type)
                except ValueError:
                    instance._logger.warning(
                        f"Invalid logical type '{config.logical_type}' for field '{field_name}'"
                    )
                    field_metadata.logical_type = instance._infer_field_logical_type(
                        field_data=field_data, field_metadata=field_metadata
                    )
            else:
                field_metadata.logical_type = instance._infer_field_logical_type(
                    field_data=field_data, field_metadata=field_metadata
                )

        # Calculate statistics
        if compute_stats:
            sample_data = field_data
            if sample_size and len(field_data) > sample_size:
                sample_data = field_data.sample(n=sample_size, random_state=42)
            field_metadata.stats = instance._calc_field_stats(
                field_data=sample_data, field_metadata=field_metadata
            )

        # Determine optimal target dtype
        if optimize_dtype:
            field_metadata.target_dtype = instance._determine_field_optimal_dtype(
                field_data=field_data, field_metadata=field_metadata
            )

        return field_metadata

    def _apply_type_hint(self, type_hint: str, current_type: DataType) -> DataType:
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

    def _infer_field_logical_type(
        self, field_data: pd.Series, field_metadata: FieldMetadata
    ) -> Optional[LogicalType]:
        """Infer logical type from data patterns"""
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
        if not self._is_string_compatible(series=sample):
            return None

        try:
            if not pd.api.types.is_string_dtype(sample):
                sample = sample.astype(str)
        except Exception:
            return None

        # Check patterns
        for logical_type, (pattern, threshold) in self.LOGICAL_TYPE_PATTERNS.items():
            try:
                matches = sample.str.match(pattern, na=False)
                match_ratio = matches.sum() / len(matches)

                if match_ratio >= threshold:
                    if logical_type in self.SPECIAL_VALIDATORS:
                        validator = self.SPECIAL_VALIDATORS[logical_type]
                        if not self._validate_with_function(
                            sample, validator, threshold
                        ):
                            continue
                    return logical_type
            except Exception as e:
                self._logger.debug(f"Pattern matching failed for {logical_type}: {e}")
                continue

        # Check categorical
        unique_ratio = field_data.nunique() / len(field_data)
        if unique_ratio < self.LOGICAL_CATEGORICAL_TYPE_PERCENTAGE:
            return LogicalType.CATEGORICAL

        return None

    def _calc_field_stats(
        self, field_data: pd.Series, field_metadata: FieldMetadata
    ) -> FieldStats:
        """Calculate field statistics"""
        stats = FieldStats(
            row_count=len(field_data),
            na_count=field_data.isna().sum(),
        )
        stats.na_percentage = round((stats.na_count / stats.row_count) * 100, 4)

        # For numeric types
        if field_metadata.data_type in [
            DataType.INT8,
            DataType.INT16,
            DataType.INT32,
            DataType.INT64,
            DataType.FLOAT32,
            DataType.FLOAT64,
        ]:
            if not field_data.dropna().empty:
                stats.min_value = field_data.min()
                stats.max_value = field_data.max()
                stats.mean_value = float(field_data.mean())
                stats.std_value = float(field_data.std())
                stats.quantiles = {
                    0.25: field_data.quantile(0.25),
                    0.5: field_data.quantile(0.5),
                    0.75: field_data.quantile(0.75),
                }

        # For all types
        stats.distinct_count = field_data.nunique()

        # Most frequent values
        value_counts = field_data.value_counts().head(10)
        if not value_counts.empty:
            stats.most_frequent = list(zip(value_counts.index, value_counts.values))

        return stats

    def _determine_field_optimal_dtype(
        self, field_data: pd.Series, field_metadata: FieldMetadata
    ) -> str:
        """Determine optimal dtype for storage"""
        if (
            field_metadata.data_type == DataType.STRING
            and field_metadata.logical_type == LogicalType.CATEGORICAL
        ):
            return "category"

        if is_numeric_dtype(field_data):
            return self._optimize_numeric_dtype(field_data)
        elif is_object_dtype(field_data):
            return self._optimize_object_dtype(field_data)

        return str(field_data.dtype)

    # Helper methods
    def _is_string_compatible(self, series: pd.Series) -> bool:
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

    def _validate_with_function(
        self, sample: pd.Series, validator: Callable, threshold: float
    ) -> bool:
        """Validate sample using a custom validator function"""
        try:
            valid_count = sum(validator(x) for x in sample)
            return (valid_count / len(sample)) >= threshold
        except Exception:
            return False

    @staticmethod
    def _validate_latitude(value: str) -> bool:
        """Validate latitude"""
        try:
            lat = float(value)
            return -90 <= lat <= 90
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _validate_longitude(value: str) -> bool:
        """Validate longitude"""
        try:
            lon = float(value)
            return -180 <= lon <= 180
        except (ValueError, TypeError):
            return False

    @staticmethod
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

    @staticmethod
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

    def _optimize_numeric_dtype(self, field_data: pd.Series) -> str:
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

    def _optimize_object_dtype(self, field_data: pd.Series) -> str:
        """Optimize object dtype"""
        if field_data.isna().all():
            return "category"

        field_data_clean = field_data.dropna()

        # Try datetime conversion
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            datetime_field_data = pd.to_datetime(field_data_clean, errors="coerce")

        if not datetime_field_data.isna().any():
            return "datetime64[s]"

        return "category"
