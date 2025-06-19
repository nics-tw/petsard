"""Metadata-level type definitions"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from petsard.metadater.schema.schema_types import SchemaConfig, SchemaMetadata


@dataclass(frozen=True)
class MetadataConfig:
    """
    Immutable configuration for metadata-level settings

    Attributes:
        metadata_id: Unique identifier for the metadata
        name: Human-readable name
        description: Description of the metadata
        schemas: Schema-specific configurations
        auto_detect_relations: Whether to automatically detect relations between schemas
        global_compute_stats: Global setting for computing statistics
        global_infer_logical_types: Global setting for logical type inference
        global_optimize_dtypes: Global setting for dtype optimization
        global_sample_size: Global sample size for inference
        properties: Additional metadata-level properties
    """

    metadata_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    schemas: Dict[str, SchemaConfig] = field(default_factory=dict)
    auto_detect_relations: bool = False
    global_compute_stats: bool = True
    global_infer_logical_types: bool = True
    global_optimize_dtypes: bool = True
    global_sample_size: Optional[int] = 1000
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration values"""
        if not self.metadata_id:
            raise ValueError("metadata_id cannot be empty")

        if self.global_sample_size is not None and self.global_sample_size <= 0:
            raise ValueError("global_sample_size must be positive or None")

        # Set default name if not provided
        if not self.name:
            object.__setattr__(self, "name", self.metadata_id)

    def get_schema_config(self, schema_id: str) -> Optional[SchemaConfig]:
        """Get schema configuration by ID"""
        return self.schemas.get(schema_id)

    def create_schema_config(
        self, schema_id: str, inherit_globals: bool = True, **kwargs: Any
    ) -> SchemaConfig:
        """Create a new schema configuration with optional global inheritance"""
        config_dict: Dict[str, Any] = {"schema_id": schema_id}

        if inherit_globals:
            global_settings: Dict[str, Any] = {
                "compute_stats": self.global_compute_stats,
                "infer_logical_types": self.global_infer_logical_types,
                "optimize_dtypes": self.global_optimize_dtypes,
                "sample_size": self.global_sample_size,
            }
            config_dict.update(global_settings)

        # Override with provided kwargs
        config_dict.update(kwargs)

        return SchemaConfig(**config_dict)

    def with_schema_config(
        self, schema_id: str, schema_config: SchemaConfig
    ) -> "MetadataConfig":
        """Create a new MetadataConfig with added/updated schema configuration"""
        new_schemas = self.schemas.copy()
        new_schemas[schema_id] = schema_config

        return MetadataConfig(
            metadata_id=self.metadata_id,
            name=self.name,
            description=self.description,
            schemas=new_schemas,
            auto_detect_relations=self.auto_detect_relations,
            global_compute_stats=self.global_compute_stats,
            global_infer_logical_types=self.global_infer_logical_types,
            global_optimize_dtypes=self.global_optimize_dtypes,
            global_sample_size=self.global_sample_size,
            properties=self.properties,
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MetadataConfig":
        """Create MetadataConfig from dictionary"""
        schemas_dict = config_dict.pop("schemas", {})
        schema_configs = {}

        for schema_id, schema_dict in schemas_dict.items():
            if isinstance(schema_dict, SchemaConfig):
                schema_configs[schema_id] = schema_dict
            elif isinstance(schema_dict, dict):
                schema_dict.setdefault("schema_id", schema_id)
                schema_configs[schema_id] = SchemaConfig.from_dict(schema_dict)
            else:
                raise ValueError(
                    f"Invalid schema config type for '{schema_id}': {type(schema_dict)}"
                )

        config_dict["schemas"] = schema_configs
        return cls(**config_dict)


@dataclass(frozen=True)
class SchemaRelation:
    """
    Represents a relationship between two schemas

    Attributes:
        from_schema: Source schema ID
        to_schema: Target schema ID
        from_field: Source field name
        to_field: Target field name
        relation_type: Type of relationship ('one_to_one', 'one_to_many', 'many_to_many')
        confidence: Confidence score of the detected relationship (0.0 to 1.0)
        properties: Additional relation properties
    """

    from_schema: str
    to_schema: str
    from_field: str
    to_field: str
    relation_type: str = "one_to_many"
    confidence: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate relation values"""
        if self.relation_type not in ["one_to_one", "one_to_many", "many_to_many"]:
            raise ValueError(f"Invalid relation_type: {self.relation_type}")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )


@dataclass(frozen=True)
class Metadata:
    """
    Immutable metadata container for multiple schemas

    Attributes:
        metadata_id: Unique identifier for the metadata
        name: Human-readable name
        description: Description of the metadata
        schemas: Dictionary of schema metadata objects
        relations: List of relationships between schemas
        properties: Additional metadata properties
        created_at: Timestamp when the metadata was created
        updated_at: Timestamp when the metadata was last updated
    """

    metadata_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    schemas: Dict[str, SchemaMetadata] = field(default_factory=dict)
    relations: List[SchemaRelation] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_schema(self, schema_id: str) -> Optional[SchemaMetadata]:
        """Get schema metadata by ID"""
        return self.schemas.get(schema_id)

    def get_schema_ids(self) -> List[str]:
        """Get list of all schema IDs"""
        return list(self.schemas.keys())

    def with_schema(self, schema: SchemaMetadata) -> "Metadata":
        """Create a new Metadata with added/updated schema"""
        new_schemas = self.schemas.copy()
        new_schemas[schema.schema_id] = schema

        return Metadata(
            metadata_id=self.metadata_id,
            name=self.name,
            description=self.description,
            schemas=new_schemas,
            relations=self.relations,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def with_relation(self, relation: SchemaRelation) -> "Metadata":
        """Create a new Metadata with added relation"""
        new_relations = self.relations + [relation]

        return Metadata(
            metadata_id=self.metadata_id,
            name=self.name,
            description=self.description,
            schemas=self.schemas,
            relations=new_relations,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def without_schema(self, schema_id: str) -> "Metadata":
        """Create a new Metadata without the specified schema"""
        new_schemas = {k: v for k, v in self.schemas.items() if k != schema_id}

        # Also remove relations involving this schema
        new_relations = [
            r
            for r in self.relations
            if r.from_schema != schema_id and r.to_schema != schema_id
        ]

        return Metadata(
            metadata_id=self.metadata_id,
            name=self.name,
            description=self.description,
            schemas=new_schemas,
            relations=new_relations,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )


# Type aliases
MetadataConfigDict = Dict[str, Any]
RelationDict = Dict[str, Any]
