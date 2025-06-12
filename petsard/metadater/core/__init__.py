"""Core functional operations for the metadater module"""

from petsard.metadater.core.field_functions import (
    build_field_metadata,
    calculate_field_stats,
    infer_field_logical_type,
    optimize_field_dtype,
)
from petsard.metadater.core.schema_functions import (
    apply_schema_transformations,
    build_schema_metadata,
    validate_schema_data,
)
from petsard.metadater.core.transformation import (
    apply_dtype_conversion,
    apply_logical_type_transformation,
    transform_field_data,
)
from petsard.metadater.core.type_inference import (
    detect_logical_type_patterns,
    infer_pandas_dtype,
    map_pandas_to_metadater_type,
)
from petsard.metadater.core.validation import (
    validate_data_against_field,
    validate_field_config,
    validate_schema_config,
)

__all__ = [
    # Field functions
    "build_field_metadata",
    "calculate_field_stats",
    "infer_field_logical_type",
    "optimize_field_dtype",
    # Schema functions
    "build_schema_metadata",
    "validate_schema_data",
    "apply_schema_transformations",
    # Type inference
    "infer_pandas_dtype",
    "map_pandas_to_metadater_type",
    "detect_logical_type_patterns",
    # Validation
    "validate_field_config",
    "validate_schema_config",
    "validate_data_against_field",
    # Transformation
    "transform_field_data",
    "apply_dtype_conversion",
    "apply_logical_type_transformation",
]
