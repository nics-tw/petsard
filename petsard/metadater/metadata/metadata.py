import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from petsard.metadater.schema.schema_types import SchemaConfig, SchemaMetadata


class RelationType(Enum):
    """
    Types of relationships between schemas
    """

    TRANSFORM = "transform"  # One schema transforms into another
    JOIN = "join"  # Two schemas are joined
    UNION = "union"  # Multiple schemas are unioned
    FILTER = "filter"  # Schema is filtered from another
    AGGREGATE = "aggregate"  # Schema is aggregated from another
    DERIVE = "derive"  # Schema is derived from another
    SOURCE = "source"  # Original source schema


@dataclass
class SchemaRelation:
    """
    Represents a relationship between schemas

    Attr.:
        from_schema_id (str): Source schema ID
        to_schema_id (str): Target schema ID
        relation_type (RelationType): Type of relationship
        description (Optional[str]): Description of the relationship
        created_at (datetime): When the relationship was created
        properties (dict[str, Any]): Additional properties (e.g., join keys, filters)
    """

    from_schema_id: str
    to_schema_id: str
    relation_type: RelationType
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Metadata:
    """
    Top-level metadata container that manages multiple schemas and their relationships

    Attr.:
        metadata_id (str): Unique identifier for the metadata
        name (str): Name of the metadata collection
        schemas (dict[str, SchemaMetadata]): dictionary of schemas by ID
        relations (list[SchemaRelation]): List of relationships between schemas
        description (Optional[str]): Description of the metadata
        created_at (datetime): When the metadata was created
        updated_at (datetime): When the metadata was last updated
        properties (dict[str, Any]): Additional metadata properties
    """

    metadata_id: str
    name: str
    schemas: dict[str, SchemaMetadata] = field(default_factory=dict)
    relations: list[SchemaRelation] = field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    properties: dict[str, Any] = field(default_factory=dict)

    def add_schema(self, schema: SchemaMetadata) -> None:
        """
        Add a schema to the metadata

        Args:
            schema (SchemaMetadata): Schema to add
        """
        if schema.schema_id in self.schemas:
            raise ValueError(f"Schema with ID {schema.schema_id} already exists")

        self.schemas[schema.schema_id] = schema
        self.updated_at = datetime.now()

    def remove_schema(self, schema_id: str) -> None:
        """
        Remove a schema and all its relationships

        Args:
            schema_id (str): ID of the schema to remove
        """
        if schema_id not in self.schemas:
            raise ValueError(f"Schema with ID {schema_id} not found")

        # Remove schema
        del self.schemas[schema_id]

        # Remove all relations involving this schema
        self.relations = [
            rel
            for rel in self.relations
            if rel.from_schema_id != schema_id and rel.to_schema_id != schema_id
        ]

        self.updated_at = datetime.now()

    def add_relation(
        self,
        from_schema_id: str,
        to_schema_id: str,
        relation_type: RelationType,
        description: Optional[str] = None,
        **properties,
    ) -> None:
        """
        Add a relationship between two schemas

        Args:
            from_schema_id (str): Source schema ID
            to_schema_id (str): Target schema ID
            relation_type (RelationType): Type of relationship
            description (Optional[str]): Description of the relationship
            **properties: Additional properties for the relationship

        Returns:
            None
        """
        # Validate schemas exist
        if from_schema_id not in self.schemas:
            raise ValueError(f"Source schema {from_schema_id} not found")
        if to_schema_id not in self.schemas:
            raise ValueError(f"Target schema {to_schema_id} not found")

        # Check if relationship already exists (including reverse)
        for existing_relation in self.relations:
            # Check direct relationship
            if (
                existing_relation.from_schema_id == from_schema_id
                and existing_relation.to_schema_id == to_schema_id
            ):
                raise ValueError(
                    f"Relationship already exists from '{from_schema_id}' to '{to_schema_id}' "
                    f"with type '{existing_relation.relation_type.value}'"
                )

            # Check reverse relationship
            if (
                existing_relation.from_schema_id == to_schema_id
                and existing_relation.to_schema_id == from_schema_id
            ):
                # Warning for reverse relationship
                warnings.warn(
                    f"Reverse relationship already exists from '{to_schema_id}' to '{from_schema_id}' "
                    f"with type '{existing_relation.relation_type.value}'. "
                    f"Consider if this new relationship is necessary.",
                    UserWarning,
                )

        # Create relation
        relation = SchemaRelation(
            from_schema_id=from_schema_id,
            to_schema_id=to_schema_id,
            relation_type=relation_type,
            description=description,
            properties=properties,
        )

        self.relations.append(relation)
        self.updated_at = datetime.now()

    def get_schema_relations(self, schema_id: str) -> dict[str, list[SchemaRelation]]:
        """
        Get all relationships for a schema

        Args:
            schema_id (str): Schema ID to get relations for

        Returns:
            dict[str, list[SchemaRelation]]: dictionary with 'incoming' and 'outgoing' relations
        """
        incoming = [rel for rel in self.relations if rel.to_schema_id == schema_id]
        outgoing = [rel for rel in self.relations if rel.from_schema_id == schema_id]

        return {"incoming": incoming, "outgoing": outgoing}

    def get_lineage(self, schema_id: str, direction: str = "upstream") -> list[str]:
        """
        Get the lineage of a schema (all connected schemas in one direction)

        Args:
            schema_id (str): Schema ID to get lineage for
            direction (str): 'upstream' (sources) or 'downstream' (derivatives)

        Returns:
            list[str]: List of schema IDs in the lineage
        """
        if schema_id not in self.schemas:
            raise ValueError(f"Schema {schema_id} not found")

        visited = set()
        to_visit = [schema_id]
        lineage = []

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue

            visited.add(current)
            lineage.append(current)

            # Get connected schemas based on direction
            if direction == "upstream":
                # Find schemas that flow into current schema
                connected = [
                    rel.from_schema_id
                    for rel in self.relations
                    if rel.to_schema_id == current and rel.from_schema_id not in visited
                ]
            else:  # downstream
                # Find schemas that current schema flows into
                connected = [
                    rel.to_schema_id
                    for rel in self.relations
                    if rel.from_schema_id == current and rel.to_schema_id not in visited
                ]

            to_visit.extend(connected)

        # Remove the starting schema from lineage
        lineage.remove(schema_id)
        return lineage

    def get_relation_graph(self) -> dict[str, set[str]]:
        """
        Get a graph representation of schema relationships

        Returns:
            dict[str, Set[str]]: dictionary mapping schema IDs to sets of connected schema IDs
        """
        graph = {schema_id: set() for schema_id in self.schemas}

        for relation in self.relations:
            graph[relation.from_schema_id].add(relation.to_schema_id)

        return graph

    def visualize_relations(self) -> str:
        """
        Create a simple text visualization of schema relationships

        Returns:
            str: Text representation of the relationships
        """
        lines = []
        lines.append(f"Metadata: {self.name}")
        lines.append(f"Schemas: {len(self.schemas)}")
        lines.append(f"Relations: {len(self.relations)}")
        lines.append("\nSchema Flow:")

        for relation in self.relations:
            arrow = "→"
            rel_type = relation.relation_type.value.upper()
            desc = f" ({relation.description})" if relation.description else ""
            lines.append(
                f"  {relation.from_schema_id} {arrow} [{rel_type}] "
                f"{arrow} {relation.to_schema_id}{desc}"
            )

        return "\n".join(lines)


@dataclass
class MetadataConfig:
    """
    Configuration for metadata-level settings

    Attr.:
        metadata_id (str): Unique identifier for the metadata collection
        name (str): Name of the metadata collection
        description (Optional[str]): Description of the metadata collection
        schemas (dict[str, SchemaConfig]): Schema-specific configurations
        auto_detect_relations (bool): Whether to automatically detect schema relationships
        relation_inference_threshold (float): Confidence threshold for relation detection
        global_compute_stats (bool): Default for computing statistics (can be overridden)
        global_infer_logical_types (bool): Default for inferring logical types
        global_optimize_dtypes (bool): Default for optimizing data types
        properties (dict[str, Any]): Additional metadata-level properties
    """

    metadata_id: str
    name: str
    description: Optional[str] = None
    schemas: dict[str, SchemaConfig] = field(default_factory=dict)
    auto_detect_relations: bool = False
    relation_inference_threshold: float = 0.8
    global_compute_stats: bool = True
    global_infer_logical_types: bool = True
    global_optimize_dtypes: bool = True
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration values"""
        if not self.metadata_id:
            raise ValueError("metadata_id cannot be empty")

        if not self.name:
            raise ValueError("name cannot be empty")

        if not 0 <= self.relation_inference_threshold <= 1:
            raise ValueError("relation_inference_threshold must be between 0 and 1")

    def add_schema_config(self, schema_config: SchemaConfig) -> None:
        """Add or update schema configuration"""
        self.schemas[schema_config.schema_id] = schema_config

    def get_schema_config(self, schema_id: str) -> Optional[SchemaConfig]:
        """Get schema configuration by ID"""
        return self.schemas.get(schema_id)

    def create_schema_config(
        self, schema_id: str, inherit_globals: bool = True, **kwargs
    ) -> SchemaConfig:
        """
        Create a new schema configuration with optional global inheritance

        Args:
            schema_id (str): ID for the new schema
            inherit_globals (bool): Whether to inherit global settings
            **kwargs: Additional parameters for SchemaConfig

        Returns:
            SchemaConfig: The created schema configuration
        """
        # Set defaults from global settings if inheriting
        if inherit_globals:
            kwargs.setdefault("compute_stats", self.global_compute_stats)
            kwargs.setdefault("infer_logical_types", self.global_infer_logical_types)
            kwargs.setdefault("optimize_dtypes", self.global_optimize_dtypes)

        schema_config = SchemaConfig(schema_id=schema_id, **kwargs)
        self.add_schema_config(schema_config)
        return schema_config

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "MetadataConfig":
        """Create MetadataConfig from dictionary"""
        # Extract schemas configuration
        schemas_dict = config_dict.pop("schemas", {})

        # Convert schema configs to SchemaConfig objects
        schema_configs = {}
        for schema_id, schema_dict in schemas_dict.items():
            if isinstance(schema_dict, SchemaConfig):
                schema_configs[schema_id] = schema_dict
            elif isinstance(schema_dict, dict):
                # Ensure schema_id is set
                schema_dict.setdefault("schema_id", schema_id)
                schema_configs[schema_id] = SchemaConfig.from_dict(schema_dict)
            else:
                raise ValueError(
                    f"Invalid schema config type for '{schema_id}': {type(schema_dict)}"
                )

        # Create MetadataConfig with remaining parameters
        config_dict["schemas"] = schema_configs
        return cls(**config_dict)
