"""Pure functions for schema-level operations"""

from typing import Any, Dict, List, Optional

import pandas as pd

from petsard.metadater.field.field_functions import build_field_metadata
from petsard.metadater.field.field_types import FieldMetadata
from petsard.metadater.schema.schema_types import (
    SchemaConfig,
    SchemaMetadata,
    SchemaStats,
)


def build_schema_metadata(
    data: pd.DataFrame,
    config: SchemaConfig,
) -> SchemaMetadata:
    """
    Pure function to build SchemaMetadata from DataFrame

    Args:
        data: DataFrame to analyze
        config: Schema configuration

    Returns:
        SchemaMetadata object
    """
    # Build field metadata for each column
    fields: List[FieldMetadata] = []

    for field_name in data.columns:
        field_config = config.get_field_config(field_name)

        # 如果沒有特定的 field_config，創建一個包含全域設定的 config
        if field_config is None:
            from petsard.metadater.field.field_types import FieldConfig

            field_config = FieldConfig(
                auto_detect_leading_zeros=config.auto_detect_leading_zeros,
                force_nullable_integers=config.force_nullable_integers,
            )
        else:
            # 如果有 field_config，但沒有設定這些參數，則使用全域設定
            if not hasattr(field_config, "auto_detect_leading_zeros"):
                # 創建新的 field_config 包含全域設定
                field_config = FieldConfig(
                    type_hint=field_config.type_hint,
                    logical_type=field_config.logical_type,
                    nullable=field_config.nullable,
                    description=field_config.description,
                    cast_error=field_config.cast_error,
                    properties=field_config.properties,
                    auto_detect_leading_zeros=config.auto_detect_leading_zeros,
                    force_nullable_integers=config.force_nullable_integers,
                )

        # Build field metadata
        field_metadata = build_field_metadata(
            field_data=data[field_name],
            field_name=field_name,
            config=field_config,
            compute_stats=config.compute_stats,
            infer_logical_type=config.infer_logical_types,
            optimize_dtype=config.optimize_dtypes,
            sample_size=config.sample_size,
        )

        fields.append(field_metadata)

    # Calculate schema-level statistics
    schema_stats = None
    if config.compute_stats:
        schema_stats = calculate_schema_stats(data, fields)

    # Create schema metadata
    schema = SchemaMetadata(
        schema_id=config.schema_id,
        name=config.name,
        description=config.description,
        fields=fields,
        stats=schema_stats,
        properties=config.properties.copy(),
    )

    return schema


def calculate_schema_stats(
    data: pd.DataFrame, fields: List[FieldMetadata]
) -> SchemaStats:
    """
    Pure function to calculate schema-level statistics

    Args:
        data: DataFrame to analyze
        fields: List of field metadata

    Returns:
        SchemaStats object
    """
    row_count = len(data)
    field_count = len(fields)

    # Calculate total null count across all fields
    total_na_count = int(data.isna().sum().sum())
    total_cells = row_count * field_count
    na_percentage = (total_na_count / total_cells * 100) if total_cells > 0 else 0.0

    return SchemaStats(
        row_count=row_count,
        field_count=field_count,
        na_count=total_na_count,
        na_percentage=round(na_percentage, 4),
    )


def validate_schema_data(
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

    # Check field presence
    schema_fields = {field.name for field in schema.fields}
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

    if extra_fields:
        warning = {
            "type": "extra_fields",
            "fields": list(extra_fields),
            "message": f"Extra fields not in schema: {extra_fields}",
        }
        warnings.append(warning)

    # Validate each field
    for field_metadata in schema.fields:
        if field_metadata.name not in data.columns:
            continue

        series = data[field_metadata.name]

        # Check nullability
        if not field_metadata.nullable and series.isna().any():
            violation = {
                "type": "null_violation",
                "field": field_metadata.name,
                "null_count": int(series.isna().sum()),
                "message": f"Field '{field_metadata.name}' contains null values but nullable=False",
            }
            violations.append(violation)

        # Check data type compatibility (if strict)
        if strict and field_metadata.source_dtype:
            expected_dtype = field_metadata.source_dtype
            actual_dtype = str(series.dtype)
            if expected_dtype != actual_dtype:
                violation = {
                    "type": "dtype_violation",
                    "field": field_metadata.name,
                    "expected": expected_dtype,
                    "actual": actual_dtype,
                    "message": f"Data type mismatch in '{field_metadata.name}': expected {expected_dtype}, got {actual_dtype}",
                }
                violations.append(violation)

    return {
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


def apply_schema_transformations(
    data: pd.DataFrame,
    schema: SchemaMetadata,
    include_fields: Optional[List[str]] = None,
    exclude_fields: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Pure function to apply schema transformations to DataFrame

    Args:
        data: DataFrame to transform
        schema: Schema metadata with transformation rules
        include_fields: Optional list of fields to include
        exclude_fields: Optional list of fields to exclude

    Returns:
        Transformed DataFrame
    """
    result = data.copy()

    # Determine which fields to process
    fields_to_process = []
    for field_metadata in schema.fields:
        if field_metadata.name not in result.columns:
            continue

        if include_fields and field_metadata.name not in include_fields:
            continue

        if exclude_fields and field_metadata.name in exclude_fields:
            continue

        fields_to_process.append(field_metadata)

    # Apply transformations to each field (simplified version)
    for field_metadata in fields_to_process:
        try:
            # Apply target dtype if specified
            if field_metadata.target_dtype and field_metadata.target_dtype != str(
                result[field_metadata.name].dtype
            ):
                if field_metadata.target_dtype == "category":
                    result[field_metadata.name] = result[field_metadata.name].astype(
                        "category"
                    )
                elif "datetime" in field_metadata.target_dtype:
                    result[field_metadata.name] = pd.to_datetime(
                        result[field_metadata.name], errors="coerce"
                    )
                else:
                    result[field_metadata.name] = result[field_metadata.name].astype(
                        field_metadata.target_dtype
                    )
        except Exception:
            # Skip transformation on error
            continue

    return result


def compare_schemas(
    schema1: SchemaMetadata,
    schema2: SchemaMetadata,
) -> Dict[str, Any]:
    """
    Pure function to compare two schemas

    Args:
        schema1: First schema
        schema2: Second schema

    Returns:
        Comparison report dictionary
    """
    schema1_fields = {field.name: field for field in schema1.fields}
    schema2_fields = {field.name: field for field in schema2.fields}

    schema1_field_names = set(schema1_fields.keys())
    schema2_field_names = set(schema2_fields.keys())

    common_fields = schema1_field_names & schema2_field_names
    only_in_schema1 = schema1_field_names - schema2_field_names
    only_in_schema2 = schema2_field_names - schema1_field_names

    # Compare common fields
    field_differences = []
    for field_name in common_fields:
        field1 = schema1_fields[field_name]
        field2 = schema2_fields[field_name]

        differences = []

        if field1.data_type != field2.data_type:
            differences.append(f"data_type: {field1.data_type} vs {field2.data_type}")

        if field1.logical_type != field2.logical_type:
            differences.append(
                f"logical_type: {field1.logical_type} vs {field2.logical_type}"
            )

        if field1.nullable != field2.nullable:
            differences.append(f"nullable: {field1.nullable} vs {field2.nullable}")

        if differences:
            field_differences.append(
                {
                    "field": field_name,
                    "differences": differences,
                }
            )

    return {
        "schemas_identical": len(field_differences) == 0
        and len(only_in_schema1) == 0
        and len(only_in_schema2) == 0,
        "common_fields": list(common_fields),
        "only_in_schema1": list(only_in_schema1),
        "only_in_schema2": list(only_in_schema2),
        "field_differences": field_differences,
        "summary": {
            "total_fields_schema1": len(schema1_field_names),
            "total_fields_schema2": len(schema2_field_names),
            "common_fields_count": len(common_fields),
            "different_fields_count": len(field_differences),
        },
    }
