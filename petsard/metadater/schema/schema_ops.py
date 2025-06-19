"""Schema-level operations and transformations"""

import logging
import warnings
from datetime import datetime
from typing import Any, Optional, Union

import pandas as pd

from petsard.metadater.datatype import DataType, LogicalType, legacy_safe_round
from petsard.metadater.field.field_ops import FieldOperations
from petsard.metadater.field.field_types import FieldMetadata
from petsard.metadater.schema.schema_types import SchemaConfig, SchemaMetadata


class SchemaOperations:
    """Operations for schema-level metadata and transformations"""

    def __init__(self):
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self.field_ops = FieldOperations()

    @classmethod
    def build_schema_from_dataframe(
        cls,
        data: pd.DataFrame,
        config: Optional[Union[SchemaConfig, dict[str, Any]]] = None,
    ) -> SchemaMetadata:
        """Build SchemaMetadata from DataFrame"""
        instance = cls()
        instance._logger.info(
            f"Building schema metadata for DataFrame with shape {data.shape}"
        )

        if config is None or not isinstance(config, SchemaConfig):
            default_schema_id: str = (
                f"default_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            if config is None:
                config = SchemaConfig(schema_id=default_schema_id)
            else:
                # Convert dict to SchemaConfig if needed
                if config is not None and not isinstance(config, SchemaConfig):
                    if isinstance(config, dict):
                        config.setdefault("schema_id", default_schema_id)
                        config = SchemaConfig.from_dict(config)
                    else:
                        raise TypeError(
                            f"config must be SchemaConfig or dict, got {type(config)}"
                        )

        # Create schema
        schema = SchemaMetadata(
            schema_id=config.schema_id, properties=config.properties.copy()
        )

        # Store config reference
        schema.properties["_config"] = config

        # Build field metadata for each column
        for field_name in data.columns:
            field_config = config.get_field_config(field_name)

            # Build field metadata
            field_metadata = instance.field_ops.build_field_from_series(
                field_data=data[field_name],
                field_name=field_name,
                config=field_config,
                compute_stats=config.compute_stats,
                infer_logical_type=config.infer_logical_types,
                optimize_dtype=config.optimize_dtypes,
                sample_size=config.sample_size,
            )

            schema.add_field(field_metadata)

        instance._logger.info(
            f"Successfully built metadata for {len(schema.fields)} fields"
        )

        return schema

    @classmethod
    def apply_field_config(
        cls,
        data: pd.DataFrame,
        schema: SchemaMetadata,
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
        raise_on_error: bool = False,
    ) -> pd.DataFrame:
        """Apply field configurations to transform data"""
        schema_ops = SchemaOperations()
        schema_ops._logger.info(
            f"Applying field configurations to DataFrame with shape {data.shape}"
        )

        result = data.copy()
        transformation_summary = {"successful": [], "failed": [], "skipped": []}

        # Determine which fields to process
        fields_to_process = []
        for field_metadata in schema.fields:
            if field_metadata.name not in result.columns:
                schema_ops._logger.warning(
                    f"Field '{field_metadata.name}' not found in DataFrame"
                )
                transformation_summary["skipped"].append(
                    {"field": field_metadata.name, "reason": "Field not in DataFrame"}
                )
                continue

            if include_fields and field_metadata.name not in include_fields:
                transformation_summary["skipped"].append(
                    {"field": field_metadata.name, "reason": "Not in include_fields"}
                )
                continue

            if exclude_fields and field_metadata.name in exclude_fields:
                transformation_summary["skipped"].append(
                    {"field": field_metadata.name, "reason": "In exclude_fields"}
                )
                continue

            fields_to_process.append(field_metadata)

        # Process each field
        for field_metadata in fields_to_process:
            try:
                original_dtype = str(result[field_metadata.name].dtype)

                # Apply transformations
                if (
                    field_metadata.target_dtype
                    and field_metadata.target_dtype != original_dtype
                ):
                    result[field_metadata.name] = schema_ops._apply_dtype_conversion(
                        field_data=result[field_metadata.name],
                        target_dtype=field_metadata.target_dtype,
                        cast_error=field_metadata.cast_error,
                        field_name=field_metadata.name,
                    )

                if field_metadata.logical_type:
                    result[field_metadata.name] = (
                        schema_ops._apply_logical_type_transformation(
                            field_data=result[field_metadata.name],
                            logical_type=field_metadata.logical_type,
                            field_metadata=field_metadata,
                        )
                    )

                if (
                    not field_metadata.nullable
                    and result[field_metadata.name].isna().any()
                ):
                    if field_metadata.cast_error == "raise":
                        raise ValueError(
                            f"Field '{field_metadata.name}' contains null values but nullable=False"
                        )
                    elif field_metadata.cast_error == "coerce":
                        result[field_metadata.name] = schema_ops._fill_nulls(
                            result[field_metadata.name], field_metadata
                        )

                transformation_summary["successful"].append(
                    {
                        "field": field_metadata.name,
                        "original_dtype": original_dtype,
                        "target_dtype": field_metadata.target_dtype,
                        "final_dtype": str(result[field_metadata.name].dtype),
                    }
                )

            except Exception as e:
                error_info = {
                    "field": field_metadata.name,
                    "error": str(e),
                    "original_dtype": original_dtype,
                }
                transformation_summary["failed"].append(error_info)

                if raise_on_error:
                    raise ValueError(
                        f"Failed to transform field '{field_metadata.name}': {e}"
                    ) from e
                else:
                    schema_ops._logger.warning(
                        f"Failed to transform field '{field_metadata.name}': {e}"
                    )

        schema_ops._logger.info(
            f"Transformation complete: "
            f"{len(transformation_summary['successful'])} successful, "
            f"{len(transformation_summary['failed'])} failed, "
            f"{len(transformation_summary['skipped'])} skipped"
        )

        result.attrs["transformation_summary"] = transformation_summary
        return result

    def validate_against_schema(
        self,
        data: pd.DataFrame,
        schema: SchemaMetadata,
        raise_on_violation: bool = True,
    ) -> dict[str, Any]:
        """Validate DataFrame against schema without transforming"""
        violations = []
        warnings = []

        schema_fields = {field_metadata.name for field_metadata in schema.fields}
        data_fields = set(data.columns)

        missing_fields = schema_fields - data_fields
        extra_fields = data_fields - schema_fields

        if missing_fields:
            violation = {
                "type": "missing_fields",
                "fields": list(missing_fields),
                "message": f"Missing required fields: {missing_fields}",
            }
            violations.append(violation)
            if raise_on_violation:
                raise ValueError(violation["message"])

        if extra_fields:
            warnings.append(
                {
                    "type": "extra_fields",
                    "fields": list(extra_fields),
                    "message": f"Extra fields not in schema: {extra_fields}",
                }
            )

        # Validate each field
        for field_metadata in schema.fields:
            if field_metadata.name not in data.columns:
                continue

            series = data[field_metadata.name]

            if not field_metadata.nullable and series.isna().any():
                violation = {
                    "type": "null_violation",
                    "field": field_metadata.name,
                    "null_count": series.isna().sum(),
                    "message": f"Field '{field_metadata.name}' contains {series.isna().sum()} null values but nullable=False",
                }
                violations.append(violation)
                if raise_on_violation:
                    raise ValueError(violation["message"])

        report = {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "summary": {
                "total_fields": len(schema.fields),
                "validated_fields": len(schema_fields & data_fields),
                "missing_fields": len(missing_fields),
                "extra_fields": len(extra_fields),
                "violations": len(violations),
                "warnings": len(warnings),
            },
        }

        return report

    def _apply_dtype_conversion(
        self, field_data: pd.Series, target_dtype: str, cast_error: str, field_name: str
    ) -> pd.Series:
        """
        Apply dtype conversion with error handling.

        Args:
            field_data (pd.Series): Series to convert
            target_dtype (str): Target data type
            cast_error (str): Error handling strategy ('raise', 'coerce', 'ignore')
            field_name (str): Field name for logging

        Returns:
            pd.Series: Converted series
        """
        if cast_error == "ignore":
            return field_data

        try:
            # Special handling for different dtype categories
            if target_dtype == "category":
                return field_data.astype("category")

            elif "datetime" in target_dtype:
                if cast_error == "coerce":
                    return pd.to_datetime(field_data, errors="coerce")
                else:
                    return pd.to_datetime(field_data)

            elif target_dtype in ["int8", "int16", "int32", "int64"]:
                if cast_error == "coerce":
                    # First convert to numeric, then to specific int type
                    numeric_field_data = pd.to_numeric(field_data, errors="coerce")
                    # Handle NaN values for integer conversion
                    if numeric_field_data.isna().any():
                        # Use nullable integer type
                        nullable_dtype = target_dtype.capitalize()
                        return numeric_field_data.astype(nullable_dtype)  # type: ignore[arg-type]
                    else:
                        return numeric_field_data.astype(target_dtype)  # type: ignore[arg-type]
                else:
                    return field_data.astype(target_dtype)  # type: ignore[arg-type]

            elif target_dtype in ["float16", "float32", "float64"]:
                if cast_error == "coerce":
                    field_data = pd.to_numeric(field_data, errors="coerce")
                    return field_data.astype(target_dtype)  # type: ignore[arg-type]
                else:
                    return field_data.astype(target_dtype)  # type: ignore[arg-type]

            elif target_dtype == "string":
                # Use pandas string dtype
                if cast_error == "coerce":
                    # Convert to string, handling any type
                    return field_data.astype(str).astype("string")
                else:
                    return field_data.astype("string")

            elif target_dtype == "boolean":
                if cast_error == "coerce":
                    # Custom boolean conversion
                    return self._coerce_to_boolean(field_data)
                else:
                    return field_data.astype("boolean")

            else:
                # Generic conversion
                if cast_error == "coerce":
                    try:
                        return field_data.astype(target_dtype)  # type: ignore[arg-type]
                    except Exception:
                        self._logger.warning(
                            f"Failed to convert '{field_name}' to {target_dtype}, keeping original"
                        )
                        return field_data
                else:
                    return field_data.astype(target_dtype)  # type: ignore[arg-type]

        except Exception as e:
            if cast_error == "raise":
                raise
            elif cast_error == "coerce":
                self._logger.warning(
                    f"Failed to convert '{field_name}' to {target_dtype}, "
                    f"keeping original dtype: {e}"
                )
                return field_data
            else:  # ignore
                return field_data

    def _apply_logical_type_transformation(
        self,
        field_data: pd.Series,
        logical_type: LogicalType,
        field_metadata: FieldMetadata,
    ) -> pd.Series:
        """
        Apply transformations based on logical type.

        Args:
            field_data (pd.Series): Series to transform
            logical_type (LogicalType): Logical type to apply
            field_metadata (FieldMetadata): Field metadata

        Returns:
            pd.Series: Transformed series
        """
        # Define transformation mappings
        transformations = {
            LogicalType.EMAIL: lambda s: s.str.lower().str.strip(),
            LogicalType.URL: lambda s: s.str.strip(),
            LogicalType.PHONE: lambda s: s.str.replace(r"[^\d+]", "", regex=True),
            LogicalType.CATEGORICAL: lambda s: s.astype("category"),
            LogicalType.CURRENCY: lambda s: self._clean_currency(s),
            LogicalType.PERCENTAGE: lambda s: self._clean_percentage(s),
            LogicalType.POSTAL_CODE: lambda s: s.str.upper().str.strip(),
            LogicalType.UUID: lambda s: s.str.lower().str.strip(),
        }

        # Apply transformation if available
        if logical_type in transformations:
            try:
                return transformations[logical_type](field_data)
            except Exception as e:
                self._logger.warning(
                    f"Failed to apply logical type transformation for '{field_metadata.name}': {e}"
                )

        return field_data

    def _fill_nulls(
        self, field_data: pd.Series, field_metadata: FieldMetadata
    ) -> pd.Series:
        """
        Fill null values based on field metadata.

        Args:
            field_data (pd.Series): Series with nulls to fill
            field_metadata (FieldMetadata): Field metadata

        Returns:
            pd.Series: Series with filled nulls
        """
        # Determine fill value based on data type
        if field_metadata.data_type in [
            DataType.INT8,
            DataType.INT16,
            DataType.INT32,
            DataType.INT64,
        ]:
            fill_value = 0
        elif field_metadata.data_type in [DataType.FLOAT32, DataType.FLOAT64]:
            fill_value = 0.0
        elif field_metadata.data_type == DataType.BOOLEAN:
            fill_value = False
        elif field_metadata.data_type == DataType.STRING:
            fill_value = ""
        elif field_metadata.data_type in [
            DataType.DATE,
            DataType.TIMESTAMP,
            DataType.TIMESTAMP_TZ,
        ]:
            fill_value = pd.NaT
        else:
            # For other types, forward fill then backward fill
            return field_data.ffill().bfill()

        return field_data.fillna(fill_value)  # type: ignore[arg-type]

    def _coerce_to_boolean(self, field_data: pd.Series) -> pd.Series:
        """
        Coerce series to boolean with flexible conversion.

        Args:
            field_data (pd.Series): Series to convert

        Returns:
            pd.Series: Boolean series
        """
        # Define truth values
        true_values = {"true", "t", "yes", "y", "1", "on", "enabled"}
        false_values = {"false", "f", "no", "n", "0", "off", "disabled"}

        # Convert to string and lowercase for comparison
        str_series = field_data.astype(str).str.lower().str.strip()

        # Create boolean series
        result = pd.Series(index=field_data.index, dtype="boolean")
        result[str_series.isin(true_values)] = True
        result[str_series.isin(false_values)] = False
        # Keep original NaN values
        result[field_data.isna()] = pd.NA

        return result

    def _clean_currency(self, field_data: pd.Series) -> pd.Series:
        """
        Clean currency values to numeric.

        Args:
            field_data (pd.Series): Series with currency values

        Returns:
            pd.Series: Numeric series
        """
        # Remove currency symbols and commas
        cleaned = field_data.astype(str).str.replace(r"[$€£¥,]", "", regex=True)
        # Convert to numeric
        return pd.to_numeric(cleaned, errors="coerce")

    def _clean_percentage(self, field_data: pd.Series) -> pd.Series:
        """
        Clean percentage values to numeric (0-1 scale).

        Args:
            field_data (pd.Series): Series with percentage values

        Returns:
            pd.Series: Numeric series (0-1 scale)
        """
        # Remove percentage sign
        cleaned = field_data.astype(str).str.replace("%", "", regex=False)
        # Convert to numeric and divide by 100
        numeric = pd.to_numeric(cleaned, errors="coerce")

        # If values are already between 0 and 1, assume they're already in decimal form
        if (numeric <= 1).all():
            return numeric
        else:
            return numeric / 100

    @classmethod
    def to_legacy_metadata_format(
        cls, data: pd.DataFrame, schema: SchemaMetadata
    ) -> dict[str, Any]:
        """
        Convert SchemaMetadata to legacy Metadata format.

        This method is deprecated and will be removed in future versions.
        It's provided for backward compatibility only.

        Args:
            data (pd.DataFrame): The original dataframe
            schema (SchemaMetadata): The schema metadata

        Returns:
            Dict[str, Any]: Legacy metadata format with 'col' and 'global' keys
        """
        warnings.warn(
            "to_legacy_metadata_format() is deprecated and will be removed in v2.0.0. "
            "Please use the new SchemaMetadata format directly. "
            "Legacy Metadata format support will be discontinued.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Initialize legacy metadata structure
        metadata = {"col": {}, "global": {}}

        # Build global metadata
        metadata["global"]["row_num"] = data.shape[0]
        metadata["global"]["col_num"] = data.shape[1]
        metadata["global"]["na_percentage"] = legacy_safe_round(
            data.isna().any(axis=1).mean()
        )

        # Build column metadata
        for field in schema.fields:
            if field.name not in data.columns:
                continue

            col_metadata = {}

            # Get pandas dtype
            col_metadata["dtype"] = data[field.name].dtype

            # Get na_percentage from stats if available, otherwise calculate
            if field.stats and hasattr(field.stats, "na_percentage"):
                col_metadata["na_percentage"] = legacy_safe_round(
                    field.stats.na_percentage / 100
                )
            else:
                col_metadata["na_percentage"] = legacy_safe_round(
                    data[field.name].isna().mean()
                )

            # Convert DataType to legacy infer_dtype
            col_metadata["infer_dtype"] = cls._convert_to_legacy_infer_dtype(
                field.data_type, field.logical_type
            )

            metadata["col"][field.name] = col_metadata

        return metadata

    @staticmethod
    def _convert_to_legacy_infer_dtype(
        data_type: DataType, logical_type: Any = None
    ) -> str:
        """
        Convert new DataType enum to legacy infer_dtype string.

        Args:
            data_type (DataType): The new DataType enum
            logical_type: The logical type (if any)

        Returns:
            str: Legacy infer_dtype value ('numerical', 'categorical', 'datetime', 'object')
        """
        # Map DataType to legacy infer_dtype
        numerical_types = {
            DataType.INT8,
            DataType.INT16,
            DataType.INT32,
            DataType.INT64,
            DataType.FLOAT32,
            DataType.FLOAT64,
            DataType.DECIMAL,
        }

        datetime_types = {
            DataType.DATE,
            DataType.TIME,
            DataType.TIMESTAMP,
            DataType.TIMESTAMP_TZ,
        }

        # Check for categorical logical type
        if (
            logical_type
            and hasattr(logical_type, "value")
            and logical_type.value == "categorical"
        ):
            return "categorical"

        # Map based on DataType
        if data_type in numerical_types:
            return "numerical"
        elif data_type in datetime_types:
            return "datetime"
        elif data_type == DataType.BOOLEAN:
            return "categorical"
        elif data_type in {DataType.STRING, DataType.BINARY}:
            # Default strings to object unless they have categorical logical type
            return "object"
        else:
            # Default fallback
            return "object"
