"""Schema-level type definitions"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from petsard.metadater.field.field_types import FieldConfig, FieldMetadata


@dataclass(frozen=True)
class SchemaStats:
    """
    Immutable statistics for the entire schema

    Attributes:
        row_count: Total number of rows in the dataset
        field_count: Total number of fields in the schema
        na_count: Total number of null values across all fields
        na_percentage: Percentage of null values across all fields
    """

    row_count: int = 0
    field_count: int = 0
    na_count: int = 0
    na_percentage: float = 0.0


@dataclass(frozen=True)
class SchemaConfig:
    """
    Immutable configuration for schema-level settings

    Attributes:
        schema_id: Unique identifier for the schema
        name: Human-readable name for the schema
        description: Description of the schema
        fields: Field-specific configurations
        compute_stats: Whether to compute statistics for fields
        infer_logical_types: Whether to automatically infer logical types
        optimize_dtypes: Whether to optimize data types for storage
        sample_size: Sample size for type inference
        auto_detect_leading_zeros: Whether to automatically detect and preserve leading zeros
        force_nullable_integers: Whether to force use of nullable integer types
        properties: Additional schema-level properties
    """

    schema_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Dict[str, FieldConfig] = field(default_factory=dict)
    compute_stats: bool = True
    infer_logical_types: bool = True
    optimize_dtypes: bool = True
    sample_size: Optional[int] = 1000
    auto_detect_leading_zeros: bool = True
    force_nullable_integers: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration values"""
        if not self.schema_id:
            raise ValueError("schema_id cannot be empty")

        if self.sample_size is not None and self.sample_size <= 0:
            raise ValueError("sample_size must be positive or None")

        # Set default name if not provided
        if not self.name:
            object.__setattr__(self, "name", self.schema_id)

    def get_field_config(self, field_name: str) -> Optional[FieldConfig]:
        """Get field configuration by name"""
        return self.fields.get(field_name)

    def with_field_config(
        self, field_name: str, field_config: FieldConfig
    ) -> "SchemaConfig":
        """Create a new SchemaConfig with added/updated field configuration"""
        new_fields = self.fields.copy()
        new_fields[field_name] = field_config

        return SchemaConfig(
            schema_id=self.schema_id,
            name=self.name,
            description=self.description,
            fields=new_fields,
            compute_stats=self.compute_stats,
            infer_logical_types=self.infer_logical_types,
            optimize_dtypes=self.optimize_dtypes,
            sample_size=self.sample_size,
            auto_detect_leading_zeros=self.auto_detect_leading_zeros,
            force_nullable_integers=self.force_nullable_integers,
            properties=self.properties,
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SchemaConfig":
        """Create SchemaConfig from dictionary"""
        fields_dict = config_dict.pop("fields", {})
        field_configs = {}

        for field_name, field_dict in fields_dict.items():
            if isinstance(field_dict, FieldConfig):
                field_configs[field_name] = field_dict
            elif isinstance(field_dict, dict):
                field_configs[field_name] = FieldConfig(**field_dict)
            else:
                raise ValueError(
                    f"Invalid field config type for '{field_name}': {type(field_dict)}"
                )

        config_dict["fields"] = field_configs
        return cls(**config_dict)


@dataclass(frozen=True)
class SchemaMetadata:
    """
    Immutable schema-level metadata

    Attributes:
        schema_id: Unique identifier for the schema
        name: Human-readable name
        description: Schema description
        fields: List of field metadata objects
        stats: Schema-level statistics
        properties: Additional properties for the schema
        created_at: Timestamp when the schema was created
        updated_at: Timestamp when the schema was last updated
    """

    schema_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    fields: List[FieldMetadata] = field(default_factory=list)
    stats: Optional[SchemaStats] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_field(self, name: str) -> Optional[FieldMetadata]:
        """Get field metadata by name"""
        for field_metadata in self.fields:
            if field_metadata.name == name:
                return field_metadata
        return None

    def get_field_names(self) -> List[str]:
        """Get list of all field names"""
        return [field_metadata.name for field_metadata in self.fields]

    def with_field(self, field_metadata: FieldMetadata) -> "SchemaMetadata":
        """Create a new SchemaMetadata with added field"""
        # Check if field already exists
        existing_field = self.get_field(field_metadata.name)
        if existing_field:
            # Replace existing field
            new_fields = [
                field_metadata if f.name == field_metadata.name else f
                for f in self.fields
            ]
        else:
            # Add new field
            new_fields = self.fields + [field_metadata]

        return SchemaMetadata(
            schema_id=self.schema_id,
            name=self.name,
            description=self.description,
            fields=new_fields,
            stats=self.stats,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def with_stats(self, stats: SchemaStats) -> "SchemaMetadata":
        """Create a new SchemaMetadata with updated stats"""
        return SchemaMetadata(
            schema_id=self.schema_id,
            name=self.name,
            description=self.description,
            fields=self.fields,
            stats=stats,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def without_field(self, field_name: str) -> "SchemaMetadata":
        """Create a new SchemaMetadata without the specified field"""
        new_fields = [f for f in self.fields if f.name != field_name]

        return SchemaMetadata(
            schema_id=self.schema_id,
            name=self.name,
            description=self.description,
            fields=new_fields,
            stats=self.stats,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def to_sdv(self) -> Dict[str, Any]:
        """
        Convert SchemaMetadata to SDV format.

        Returns:
            dict: Metadata in SDV format
        """
        from petsard.metadater.adapters.sdv_adapter import SDVMetadataAdapter

        adapter = SDVMetadataAdapter()
        return adapter.convert_to_sdv_dict(self)


# Type aliases
SchemaConfigDict = Dict[str, Any]
SchemaMetadataDict = Dict[str, SchemaMetadata]
