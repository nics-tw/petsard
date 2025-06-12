# New functional programming interface (recommended)
from petsard.metadater.api import (
    FieldPipeline,
    analyze_dataframe_fields,
    analyze_field,
    compose,
    create_field_analyzer,
    create_schema_from_dataframe,
    pipe,
    validate_field_data,
)

# Core functional operations
from petsard.metadater.core.field_functions import (
    build_field_metadata,
    calculate_field_stats,
    infer_field_logical_type,
    optimize_field_dtype,
)

# Legacy compatibility (deprecated)
from petsard.metadater.field_meta import FieldConfig as LegacyFieldConfig
from petsard.metadater.field_meta import FieldMetadata as LegacyFieldMetadata
from petsard.metadater.field_ops import FieldOperations
from petsard.metadater.metadata import Metadata as LegacyMetadata
from petsard.metadater.metadater import Metadater
from petsard.metadater.schema_meta import SchemaConfig as LegacySchemaConfig
from petsard.metadater.schema_meta import SchemaMetadata as LegacySchemaMetadata
from petsard.metadater.schema_ops import SchemaOperations

# Type definitions
from petsard.metadater.types import (
    DataType,
    FieldConfig,
    FieldMetadata,
    FieldStats,
    LogicalType,
    Metadata,
    MetadataConfig,
    SchemaConfig,
    SchemaMetadata,
    SchemaStats,
)

__all__ = [
    # Functional API (recommended)
    "analyze_field",
    "analyze_dataframe_fields",
    "create_field_analyzer",
    "create_schema_from_dataframe",
    "compose",
    "pipe",
    "FieldPipeline",
    "validate_field_data",
    # Type definitions
    "DataType",
    "LogicalType",
    "FieldConfig",
    "FieldMetadata",
    "FieldStats",
    "SchemaConfig",
    "SchemaMetadata",
    "SchemaStats",
    "Metadata",
    "MetadataConfig",
    # Core functions
    "build_field_metadata",
    "calculate_field_stats",
    "infer_field_logical_type",
    "optimize_field_dtype",
    # Legacy compatibility (deprecated)
    "Metadater",
    "FieldOperations",
    "SchemaOperations",
    "LegacyMetadata",
    "LegacySchemaMetadata",
    "LegacyFieldMetadata",
    "LegacySchemaConfig",
    "LegacyFieldConfig",
]
