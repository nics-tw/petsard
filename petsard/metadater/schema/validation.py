"""Pure functions for validation operations"""

from typing import Any, Dict, List

import pandas as pd

from petsard.metadater.field.field_types import FieldConfig, FieldMetadata
from petsard.metadater.schema.schema_types import SchemaConfig, SchemaMetadata
from petsard.metadater.types.data_types import DataType, LogicalType


def validate_field_config(config: FieldConfig) -> Dict[str, Any]:
    """
    Pure function to validate field configuration

    Args:
        config: Field configuration to validate

    Returns:
        Validation report dictionary
    """
    violations = []
    warnings = []

    # Validate cast_error values
    if config.cast_error not in ["raise", "coerce", "ignore"]:
        violations.append(
            {
                "type": "invalid_cast_error",
                "value": config.cast_error,
                "message": f"Invalid cast_error value: {config.cast_error}. Must be 'raise', 'coerce', or 'ignore'",
            }
        )

    # Validate logical_type if specified
    if config.logical_type is not None:
        try:
            if isinstance(config.logical_type, str):
                LogicalType(config.logical_type)
            elif not isinstance(config.logical_type, LogicalType):
                violations.append(
                    {
                        "type": "invalid_logical_type",
                        "value": config.logical_type,
                        "message": f"Invalid logical_type: {config.logical_type}",
                    }
                )
        except ValueError:
            violations.append(
                {
                    "type": "invalid_logical_type",
                    "value": config.logical_type,
                    "message": f"Unknown logical_type: {config.logical_type}",
                }
            )

    # Validate type_hint if specified
    if config.type_hint is not None:
        valid_type_hints = [
            "category",
            "datetime",
            "date",
            "time",
            "int",
            "integer",
            "float",
            "string",
            "boolean",
        ]
        if config.type_hint.lower() not in valid_type_hints:
            warnings.append(
                {
                    "type": "unknown_type_hint",
                    "value": config.type_hint,
                    "message": f"Unknown type_hint: {config.type_hint}. Valid hints: {valid_type_hints}",
                }
            )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
    }


def validate_schema_config(config: SchemaConfig) -> Dict[str, Any]:
    """
    Pure function to validate schema configuration

    Args:
        config: Schema configuration to validate

    Returns:
        Validation report dictionary
    """
    violations = []
    warnings = []

    # Validate schema_id
    if not config.schema_id or not config.schema_id.strip():
        violations.append(
            {
                "type": "empty_schema_id",
                "message": "schema_id cannot be empty",
            }
        )

    # Validate sample_size
    if config.sample_size is not None and config.sample_size <= 0:
        violations.append(
            {
                "type": "invalid_sample_size",
                "value": config.sample_size,
                "message": f"sample_size must be positive or None, got {config.sample_size}",
            }
        )

    # Validate field configurations
    field_violations = []
    for field_name, field_config in config.fields.items():
        field_validation = validate_field_config(field_config)
        if not field_validation["valid"]:
            field_violations.append(
                {
                    "field": field_name,
                    "violations": field_validation["violations"],
                    "warnings": field_validation["warnings"],
                }
            )

    if field_violations:
        violations.append(
            {
                "type": "invalid_field_configs",
                "field_violations": field_violations,
                "message": f"Invalid field configurations found in {len(field_violations)} fields",
            }
        )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
    }


def validate_data_against_field(
    data: pd.Series,
    field_metadata: FieldMetadata,
    strict: bool = False,
) -> Dict[str, Any]:
    """
    Pure function to validate data against field metadata

    Args:
        data: Series to validate
        field_metadata: Field metadata to validate against
        strict: Whether to use strict validation

    Returns:
        Validation report dictionary
    """
    violations = []
    warnings = []

    # Check nullability
    null_count = data.isna().sum()
    if not field_metadata.nullable and null_count > 0:
        violations.append(
            {
                "type": "null_violation",
                "field": field_metadata.name,
                "null_count": int(null_count),
                "total_count": len(data),
                "message": f"Field '{field_metadata.name}' contains {null_count} null values but nullable=False",
            }
        )

    # Check data type compatibility
    if field_metadata.source_dtype:
        expected_dtype = field_metadata.source_dtype
        actual_dtype = str(data.dtype)

        if strict and expected_dtype != actual_dtype:
            violations.append(
                {
                    "type": "dtype_violation",
                    "field": field_metadata.name,
                    "expected": expected_dtype,
                    "actual": actual_dtype,
                    "message": f"Data type mismatch: expected {expected_dtype}, got {actual_dtype}",
                }
            )
        elif expected_dtype != actual_dtype:
            warnings.append(
                {
                    "type": "dtype_mismatch",
                    "field": field_metadata.name,
                    "expected": expected_dtype,
                    "actual": actual_dtype,
                    "message": f"Data type mismatch: expected {expected_dtype}, got {actual_dtype}",
                }
            )

    # Validate logical type constraints
    if field_metadata.logical_type:
        logical_violations = _validate_logical_type_constraints(
            data, field_metadata.logical_type
        )
        violations.extend(logical_violations)

    # Check value ranges for numeric types
    if field_metadata.data_type in [
        DataType.INT8,
        DataType.INT16,
        DataType.INT32,
        DataType.INT64,
        DataType.FLOAT32,
        DataType.FLOAT64,
    ]:
        range_violations = _validate_numeric_ranges(data, field_metadata)
        violations.extend(range_violations)

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "field_name": field_metadata.name,
        "summary": {
            "total_rows": len(data),
            "null_rows": int(null_count),
            "valid_rows": len(data) - int(null_count),
            "violations_count": len(violations),
            "warnings_count": len(warnings),
        },
    }


def validate_dataframe_against_schema(
    data: pd.DataFrame,
    schema: SchemaMetadata,
    strict: bool = False,
) -> Dict[str, Any]:
    """
    Pure function to validate DataFrame against schema

    Args:
        data: DataFrame to validate
        schema: Schema metadata to validate against
        strict: Whether to use strict validation

    Returns:
        Validation report dictionary
    """
    violations = []
    warnings = []
    field_reports = []

    # Check schema-level constraints
    schema_fields = {field.name for field in schema.fields}
    data_fields = set(data.columns)

    missing_fields = schema_fields - data_fields
    extra_fields = data_fields - schema_fields

    if missing_fields:
        violations.append(
            {
                "type": "missing_fields",
                "fields": list(missing_fields),
                "message": f"Missing required fields: {missing_fields}",
            }
        )

    if extra_fields:
        if strict:
            violations.append(
                {
                    "type": "extra_fields",
                    "fields": list(extra_fields),
                    "message": f"Extra fields not allowed in strict mode: {extra_fields}",
                }
            )
        else:
            warnings.append(
                {
                    "type": "extra_fields",
                    "fields": list(extra_fields),
                    "message": f"Extra fields found: {extra_fields}",
                }
            )

    # Validate each field
    for field_metadata in schema.fields:
        if field_metadata.name not in data.columns:
            continue

        field_report = validate_data_against_field(
            data=data[field_metadata.name],
            field_metadata=field_metadata,
            strict=strict,
        )

        field_reports.append(field_report)

        # Aggregate field violations to schema level
        if field_report["violations"]:
            violations.extend(field_report["violations"])
        if field_report["warnings"]:
            warnings.extend(field_report["warnings"])

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "field_reports": field_reports,
        "summary": {
            "total_fields": len(schema.fields),
            "validated_fields": len([r for r in field_reports if r["valid"]]),
            "missing_fields": len(missing_fields),
            "extra_fields": len(extra_fields),
            "total_violations": len(violations),
            "total_warnings": len(warnings),
            "data_shape": data.shape,
        },
    }


def validate_field_metadata_consistency(
    field_metadata: FieldMetadata,
) -> Dict[str, Any]:
    """
    Pure function to validate internal consistency of field metadata

    Args:
        field_metadata: Field metadata to validate

    Returns:
        Validation report dictionary
    """
    violations = []
    warnings = []

    # Check data type and logical type compatibility
    if field_metadata.logical_type:
        compatibility_violations = _check_datatype_logical_type_compatibility(
            field_metadata.data_type, field_metadata.logical_type
        )
        violations.extend(compatibility_violations)

    # Check stats consistency
    if field_metadata.stats:
        stats_violations = _validate_field_stats_consistency(field_metadata.stats)
        violations.extend(stats_violations)

    # Check target dtype compatibility
    if field_metadata.target_dtype and field_metadata.source_dtype:
        if not _are_dtypes_compatible(
            field_metadata.source_dtype, field_metadata.target_dtype
        ):
            warnings.append(
                {
                    "type": "dtype_conversion_warning",
                    "source": field_metadata.source_dtype,
                    "target": field_metadata.target_dtype,
                    "message": f"Conversion from {field_metadata.source_dtype} to {field_metadata.target_dtype} may lose precision",
                }
            )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "field_name": field_metadata.name,
    }


# Helper functions


def _validate_logical_type_constraints(
    data: pd.Series, logical_type: LogicalType
) -> List[Dict[str, Any]]:
    """Validate data against logical type constraints"""
    violations = []

    if logical_type == LogicalType.EMAIL:
        invalid_emails = _find_invalid_emails(data)
        if invalid_emails:
            violations.append(
                {
                    "type": "invalid_email_format",
                    "invalid_count": len(invalid_emails),
                    "examples": invalid_emails[:5],  # Show first 5 examples
                    "message": f"Found {len(invalid_emails)} invalid email addresses",
                }
            )

    elif logical_type == LogicalType.URL:
        invalid_urls = _find_invalid_urls(data)
        if invalid_urls:
            violations.append(
                {
                    "type": "invalid_url_format",
                    "invalid_count": len(invalid_urls),
                    "examples": invalid_urls[:5],
                    "message": f"Found {len(invalid_urls)} invalid URLs",
                }
            )

    elif logical_type in [LogicalType.LATITUDE, LogicalType.LONGITUDE]:
        invalid_coords = _find_invalid_coordinates(data, logical_type)
        if invalid_coords:
            violations.append(
                {
                    "type": f"invalid_{logical_type.value}",
                    "invalid_count": len(invalid_coords),
                    "examples": invalid_coords[:5],
                    "message": f"Found {len(invalid_coords)} invalid {logical_type.value} values",
                }
            )

    return violations


def _validate_numeric_ranges(
    data: pd.Series, field_metadata: FieldMetadata
) -> List[Dict[str, Any]]:
    """Validate numeric data against expected ranges"""
    violations = []

    if field_metadata.data_type == DataType.INT8:
        out_of_range = data[(data < -128) | (data > 127)].dropna()
    elif field_metadata.data_type == DataType.INT16:
        out_of_range = data[(data < -32768) | (data > 32767)].dropna()
    elif field_metadata.data_type == DataType.INT32:
        out_of_range = data[(data < -2147483648) | (data > 2147483647)].dropna()
    else:
        return violations  # No range check for other types

    if len(out_of_range) > 0:
        violations.append(
            {
                "type": "numeric_range_violation",
                "data_type": field_metadata.data_type.value,
                "out_of_range_count": len(out_of_range),
                "examples": out_of_range.head(5).tolist(),
                "message": f"Found {len(out_of_range)} values outside valid range for {field_metadata.data_type.value}",
            }
        )

    return violations


def _check_datatype_logical_type_compatibility(
    data_type: DataType, logical_type: LogicalType
) -> List[Dict[str, Any]]:
    """Check compatibility between data type and logical type"""
    violations = []

    # Define compatibility rules
    string_logical_types = {
        LogicalType.EMAIL,
        LogicalType.URL,
        LogicalType.UUID,
        LogicalType.PHONE,
        LogicalType.POSTAL_CODE,
        LogicalType.CATEGORICAL,
    }

    numeric_logical_types = {
        LogicalType.LATITUDE,
        LogicalType.LONGITUDE,
        LogicalType.PERCENTAGE,
        LogicalType.CURRENCY,
    }

    if logical_type in string_logical_types and data_type not in [
        DataType.STRING,
        DataType.BINARY,
    ]:
        violations.append(
            {
                "type": "incompatible_data_logical_type",
                "data_type": data_type.value,
                "logical_type": logical_type.value,
                "message": f"Logical type {logical_type.value} requires string data type, got {data_type.value}",
            }
        )

    elif logical_type in numeric_logical_types and data_type not in [
        DataType.INT8,
        DataType.INT16,
        DataType.INT32,
        DataType.INT64,
        DataType.FLOAT32,
        DataType.FLOAT64,
        DataType.DECIMAL,
    ]:
        violations.append(
            {
                "type": "incompatible_data_logical_type",
                "data_type": data_type.value,
                "logical_type": logical_type.value,
                "message": f"Logical type {logical_type.value} requires numeric data type, got {data_type.value}",
            }
        )

    return violations


def _validate_field_stats_consistency(stats) -> List[Dict[str, Any]]:
    """Validate internal consistency of field statistics"""
    violations = []

    # Check basic consistency
    if stats.na_count > stats.row_count:
        violations.append(
            {
                "type": "inconsistent_stats",
                "message": f"na_count ({stats.na_count}) cannot be greater than row_count ({stats.row_count})",
            }
        )

    if stats.distinct_count > stats.row_count:
        violations.append(
            {
                "type": "inconsistent_stats",
                "message": f"distinct_count ({stats.distinct_count}) cannot be greater than row_count ({stats.row_count})",
            }
        )

    # Check percentage calculation
    if stats.row_count > 0:
        expected_na_percentage = (stats.na_count / stats.row_count) * 100
        if (
            abs(stats.na_percentage - expected_na_percentage) > 0.01
        ):  # Allow small rounding errors
            violations.append(
                {
                    "type": "inconsistent_stats",
                    "message": f"na_percentage ({stats.na_percentage}) doesn't match calculated value ({expected_na_percentage:.4f})",
                }
            )

    return violations


def _are_dtypes_compatible(source_dtype: str, target_dtype: str) -> bool:
    """Check if dtype conversion is safe"""
    # Define safe conversions
    safe_conversions = {
        "int8": ["int16", "int32", "int64", "float32", "float64"],
        "int16": ["int32", "int64", "float32", "float64"],
        "int32": ["int64", "float64"],
        "int64": ["float64"],
        "float32": ["float64"],
        "object": ["string", "category"],
    }

    return target_dtype in safe_conversions.get(source_dtype, [target_dtype])


def _find_invalid_emails(data: pd.Series) -> List[str]:
    """Find invalid email addresses in series"""
    import re

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    invalid_emails = []
    for value in data.dropna():
        if not re.match(email_pattern, str(value)):
            invalid_emails.append(str(value))

    return invalid_emails


def _find_invalid_urls(data: pd.Series) -> List[str]:
    """Find invalid URLs in series"""
    import re

    url_pattern = r"^https?://[^\s]+$"

    invalid_urls = []
    for value in data.dropna():
        if not re.match(url_pattern, str(value)):
            invalid_urls.append(str(value))

    return invalid_urls


def _find_invalid_coordinates(data: pd.Series, coord_type: LogicalType) -> List[float]:
    """Find invalid coordinate values"""
    invalid_coords = []

    for value in data.dropna():
        try:
            coord_value = float(value)
            if coord_type == LogicalType.LATITUDE:
                if not (-90 <= coord_value <= 90):
                    invalid_coords.append(coord_value)
            elif coord_type == LogicalType.LONGITUDE:
                if not (-180 <= coord_value <= 180):
                    invalid_coords.append(coord_value)
        except (ValueError, TypeError):
            invalid_coords.append(value)

    return invalid_coords
