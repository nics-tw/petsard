"""Schema-level metadata classes and data structures"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from petsard.metadater.field_meta import FieldMetadata


@dataclass
class SchemaStats:
    """
    Statistics for the entire schema

    Attr.:
        row_count (int): Total number of rows in the dataset
        field_count (int): Total number of fields in the schema
        na_count (int): Total number of null values across all fields
        na_percentage (float): Percentage of null values across all fields
    """

    row_count: int = 0
    field_count: int = 0
    na_count: int = 0
    na_percentage: float = 0.0


@dataclass
class SchemaMetadata:
    """
    Schema-level metadata

    Attr.:
        schema_id (str): Unique identifier for the schema
        created_at (datetime): Timestamp when the schema was created
        updated_at (datetime): Timestamp when the schema was last updated
        fields (list[FieldMetadata]): List of field metadata objects
        properties (dict[str, Any]): Additional properties for the schema
    """

    schema_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    fields: list[FieldMetadata] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)

    def get_field(self, name: str) -> Optional[FieldMetadata]:
        """Get field metadata by name"""
        for field_metadata in self.fields:
            if field_metadata.name == name:
                return field_metadata
        return None

    def add_field(self, field_metadata: FieldMetadata) -> None:
        """Add a new field to schema"""
        if self.get_field(field_metadata.name):
            raise ValueError(f"Field {field_metadata.name} already exists in schema")
        self.fields.append(field_metadata)
        self.updated_at = datetime.now()

    def to_sdv(self) -> dict:
        """
        Convert SchemaMetadata to SDV format.

        Returns:
            dict: Metadata in SDV format
        """
        if not self.fields:
            raise ValueError("No fields found in SchemaMetadata")

        sdv_metadata = {"columns": {}}

        for field_metadata in self.fields:
            data_type = field_metadata.data_type

            # Map DataType to SDV sdtype
            if hasattr(data_type, "value"):
                data_type_str = data_type.value.lower()
            else:
                data_type_str = str(data_type).lower()

            # Map specific DataType values to SDV categories
            if data_type_str in [
                "int8",
                "int16",
                "int32",
                "int64",
                "float32",
                "float64",
                "decimal",
            ]:
                sdtype = "numerical"
            elif data_type_str == "boolean":
                sdtype = "categorical"  # SDV treats boolean as categorical
            elif data_type_str in ["date", "time", "timestamp", "timestamp_tz"]:
                sdtype = "datetime"
            elif data_type_str in ["string", "binary"]:
                # Check logical type for better classification
                if (
                    field_metadata.logical_type
                    and hasattr(field_metadata.logical_type, "value")
                    and field_metadata.logical_type.value.lower() == "categorical"
                ):
                    sdtype = "categorical"
                else:
                    sdtype = "categorical"  # Default string to categorical for SDV
            else:
                sdtype = "categorical"  # Fallback to categorical

            sdv_metadata["columns"][field_metadata.name] = {"sdtype": sdtype}

        return sdv_metadata


@dataclass
class SchemaConfig:
    """
    Configuration for schema-level settings

    Attr.:
        schema_id (str): Unique identifier for the schema
        name (Optional[str]): Human-readable name for the schema
        description (Optional[str]): Description of the schema
        fields (dict[str, FieldConfig]): Field-specific configurations
        compute_stats (bool): Whether to compute statistics for fields
        infer_logical_types (bool): Whether to automatically infer logical types
        optimize_dtypes (bool): Whether to optimize data types for storage
        sample_size (Optional[int]): Sample size for type inference
        properties (dict[str, Any]): Additional schema-level properties
    """

    schema_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    fields: dict[str, Any] = field(default_factory=dict)  # Will store FieldConfig
    compute_stats: bool = True
    infer_logical_types: bool = True
    optimize_dtypes: bool = True
    sample_size: Optional[int] = 1000
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration values"""
        if not self.schema_id:
            raise ValueError("schema_id cannot be empty")

        if self.sample_size is not None and self.sample_size <= 0:
            raise ValueError("sample_size must be positive or None")

        if not self.name:
            self.name = self.schema_id

    def add_field_config(self, field_name: str, field_config: Any) -> None:
        """Add or update field configuration"""
        self.fields[field_name] = field_config

    def get_field_config(self, field_name: str) -> Optional[Any]:
        """Get field configuration by name"""
        return self.fields.get(field_name)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "SchemaConfig":
        """Create SchemaConfig from dictionary"""
        from petsard.metadater.field_meta import FieldConfig

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
