"""High-level functional API for the metadater module"""

from functools import partial
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from petsard.metadater.field.field_functions import (
    build_field_metadata,
    calculate_field_stats,
)
from petsard.metadater.field.field_ops import optimize_field_dtype
from petsard.metadater.field.type_inference import infer_field_logical_type
from petsard.metadater.types.data_types import LogicalType
from petsard.metadater.types.field_types import FieldConfig, FieldMetadata, FieldStats


# Functional composition utilities
def compose(*functions: Callable) -> Callable:
    """Compose functions from right to left"""
    return lambda x: _reduce_functions(functions, x)


def pipe(value: Any, *functions: Callable) -> Any:
    """Apply functions from left to right (pipeline style)"""
    return _reduce_functions(functions, value)


def _reduce_functions(functions: tuple, initial_value: Any) -> Any:
    """Helper to reduce functions over a value"""
    result = initial_value
    for func in functions:
        result = func(result)
    return result


# High-level field operations
def analyze_field(
    field_data: pd.Series,
    field_name: str,
    config: Optional[FieldConfig] = None,
    **options: Any,
) -> FieldMetadata:
    """
    High-level function to analyze a field with all features

    Args:
        field_data: The pandas Series to analyze
        field_name: Name of the field
        config: Optional field configuration
        **options: Additional options (compute_stats, infer_logical_type, etc.)

    Returns:
        Complete FieldMetadata
    """
    return build_field_metadata(
        field_data=field_data, field_name=field_name, config=config, **options
    )


def create_field_analyzer(
    compute_stats: bool = True,
    infer_logical_type: bool = True,
    optimize_dtype: bool = True,
    sample_size: Optional[int] = 1000,
) -> Callable[[pd.Series, str, Optional[FieldConfig]], FieldMetadata]:
    """
    Create a configured field analyzer function

    Args:
        compute_stats: Whether to compute statistics
        infer_logical_type: Whether to infer logical type
        optimize_dtype: Whether to optimize dtype
        sample_size: Sample size for analysis

    Returns:
        Configured analyzer function
    """
    return partial(
        build_field_metadata,
        compute_stats=compute_stats,
        infer_logical_type=infer_logical_type,
        optimize_dtype=optimize_dtype,
        sample_size=sample_size,
    )


def create_stats_calculator() -> Callable[[pd.Series, FieldMetadata], FieldStats]:
    """Create a stats calculator function"""
    return calculate_field_stats


def create_logical_type_inferrer() -> Callable[
    [pd.Series, FieldMetadata], Optional[LogicalType]
]:
    """Create a logical type inferrer function"""
    return infer_field_logical_type


def create_dtype_optimizer() -> Callable[[pd.Series, FieldMetadata], str]:
    """Create a dtype optimizer function"""
    return optimize_field_dtype


# Functional field processing pipeline
class FieldPipeline:
    """Functional pipeline for field processing"""

    def __init__(self):
        self._steps: List[Callable] = []

    def add_step(self, step: Callable) -> "FieldPipeline":
        """Add a processing step to the pipeline"""
        self._steps.append(step)
        return self

    def with_stats(self, enabled: bool = True) -> "FieldPipeline":
        """Add stats calculation step"""
        if enabled:
            self._steps.append(
                lambda metadata, data: metadata.with_stats(
                    calculate_field_stats(data, metadata)
                )
            )
        return self

    def with_logical_type_inference(self, enabled: bool = True) -> "FieldPipeline":
        """Add logical type inference step"""
        if enabled:

            def infer_step(metadata: FieldMetadata, data: pd.Series) -> FieldMetadata:
                logical_type = infer_field_logical_type(data, metadata)
                return (
                    metadata.with_logical_type(logical_type)
                    if logical_type
                    else metadata
                )

            self._steps.append(infer_step)
        return self

    def with_dtype_optimization(self, enabled: bool = True) -> "FieldPipeline":
        """Add dtype optimization step"""
        if enabled:
            self._steps.append(
                lambda metadata, data: metadata.with_target_dtype(
                    optimize_field_dtype(data, metadata)
                )
            )
        return self

    def process(
        self, field_data: pd.Series, initial_metadata: FieldMetadata
    ) -> FieldMetadata:
        """Process field through the pipeline"""
        result = initial_metadata
        for step in self._steps:
            result = step(result, field_data)
        return result


# Schema-level functional operations
def analyze_dataframe_fields(
    data: pd.DataFrame,
    field_configs: Optional[Dict[str, FieldConfig]] = None,
    analyzer: Optional[Callable] = None,
) -> Dict[str, FieldMetadata]:
    """
    Analyze all fields in a DataFrame using functional approach

    Args:
        data: DataFrame to analyze
        field_configs: Optional field configurations
        analyzer: Optional custom analyzer function

    Returns:
        Dictionary of field metadata
    """
    if analyzer is None:
        analyzer = create_field_analyzer()

    if field_configs is None:
        field_configs = {}

    results = {}
    for column in data.columns:
        config = field_configs.get(column)
        results[column] = analyzer(data[column], column, config)

    return results


# Functional validation
def validate_field_data(
    field_data: pd.Series,
    field_metadata: FieldMetadata,
    strict: bool = False,
) -> Dict[str, Any]:
    """
    Validate field data against metadata

    Args:
        field_data: Series to validate
        field_metadata: Metadata to validate against
        strict: Whether to use strict validation

    Returns:
        Validation report
    """
    violations = []
    warnings = []

    # Check nullability
    if not field_metadata.nullable and field_data.isna().any():
        violation = {
            "type": "null_violation",
            "field": field_metadata.name,
            "null_count": field_data.isna().sum(),
            "message": "Field contains null values but nullable=False",
        }
        violations.append(violation)

    # Check data type compatibility
    expected_dtype = field_metadata.source_dtype
    actual_dtype = str(field_data.dtype)
    if expected_dtype and expected_dtype != actual_dtype:
        warning = {
            "type": "dtype_mismatch",
            "field": field_metadata.name,
            "expected": expected_dtype,
            "actual": actual_dtype,
            "message": f"Data type mismatch: expected {expected_dtype}, got {actual_dtype}",
        }
        warnings.append(warning)

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "field_name": field_metadata.name,
    }


# Export main functional interface
__all__ = [
    # Composition utilities
    "compose",
    "pipe",
    # Field operations
    "analyze_field",
    "create_field_analyzer",
    "create_stats_calculator",
    "create_logical_type_inferrer",
    "create_dtype_optimizer",
    # Pipeline
    "FieldPipeline",
    # Schema operations
    "analyze_dataframe_fields",
    # Validation
    "validate_field_data",
]
