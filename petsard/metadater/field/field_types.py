"""Field-level type definitions"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from petsard.metadater.types.data_types import DataType, LogicalType


@dataclass(frozen=True)
class FieldStats:
    """
    Immutable statistics for a field

    Attributes:
        row_count: Total number of rows
        na_count: Number of null/missing values
        na_percentage: Percentage of null values
        distinct_count: Number of unique values
        min_value: Minimum value (for numeric types)
        max_value: Maximum value (for numeric types)
        mean_value: Mean value (for numeric types)
        std_value: Standard deviation (for numeric types)
        quantiles: Quantile values (for numeric types)
        most_frequent: Most frequent values and their counts
    """

    row_count: int = 0
    na_count: int = 0
    na_percentage: float = 0.0
    distinct_count: int = 0
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    mean_value: Optional[float] = None
    std_value: Optional[float] = None
    quantiles: Optional[Dict[float, Union[int, float]]] = None
    most_frequent: Optional[List[Tuple[Any, int]]] = None


@dataclass(frozen=True)
class FieldConfig:
    """
    Immutable configuration for field processing

    Attributes:
        type_hint: Hint for data type inference
        logical_type: Logical type for the field
        nullable: Whether the field can contain null values
        description: Human-readable description
        cast_error: Error handling strategy ('raise', 'coerce', 'ignore')
        auto_detect_leading_zeros: Whether to automatically detect and preserve leading zeros
        force_nullable_integers: Whether to force use of nullable integer types
        properties: Additional field properties
    """

    type_hint: Optional[str] = None
    logical_type: Optional[Union[LogicalType, str]] = None
    nullable: Optional[bool] = None
    description: Optional[str] = None
    cast_error: str = "coerce"
    auto_detect_leading_zeros: bool = True
    force_nullable_integers: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.cast_error not in ["raise", "coerce", "ignore"]:
            raise ValueError(f"Invalid cast_error: {self.cast_error}")


@dataclass(frozen=True)
class FieldMetadata:
    """
    Immutable metadata for a single field

    Attributes:
        name: Field name
        data_type: Basic data type
        logical_type: Logical/semantic type
        nullable: Whether field can contain nulls
        source_dtype: Original pandas dtype
        target_dtype: Optimized target dtype
        description: Field description
        cast_error: Error handling strategy
        stats: Field statistics
        properties: Additional properties
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    name: str
    data_type: DataType
    logical_type: Optional[LogicalType] = None
    nullable: bool = True
    source_dtype: Optional[str] = None
    target_dtype: Optional[str] = None
    description: Optional[str] = None
    cast_error: str = "coerce"
    stats: Optional[FieldStats] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def with_stats(self, stats: FieldStats) -> "FieldMetadata":
        """Create a new FieldMetadata with updated stats"""
        return FieldMetadata(
            name=self.name,
            data_type=self.data_type,
            logical_type=self.logical_type,
            nullable=self.nullable,
            source_dtype=self.source_dtype,
            target_dtype=self.target_dtype,
            description=self.description,
            cast_error=self.cast_error,
            stats=stats,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def with_target_dtype(self, target_dtype: str) -> "FieldMetadata":
        """Create a new FieldMetadata with updated target dtype"""
        return FieldMetadata(
            name=self.name,
            data_type=self.data_type,
            logical_type=self.logical_type,
            nullable=self.nullable,
            source_dtype=self.source_dtype,
            target_dtype=target_dtype,
            description=self.description,
            cast_error=self.cast_error,
            stats=self.stats,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def with_logical_type(self, logical_type: LogicalType) -> "FieldMetadata":
        """Create a new FieldMetadata with updated logical type"""
        return FieldMetadata(
            name=self.name,
            data_type=self.data_type,
            logical_type=logical_type,
            nullable=self.nullable,
            source_dtype=self.source_dtype,
            target_dtype=self.target_dtype,
            description=self.description,
            cast_error=self.cast_error,
            stats=self.stats,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )


# Type aliases
FieldConfigDict = Dict[str, Any]
FieldMetadataDict = Dict[str, FieldMetadata]
