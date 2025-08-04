"""Field-level type definitions"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

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
    min_value: int | float | None = None
    max_value: int | float | None = None
    mean_value: float | None = None
    std_value: float | None = None
    quantiles: dict[float, int | float] | None = None
    most_frequent: list[tuple[Any, int]] | None = None


@dataclass(frozen=True)
class FieldConfig:
    """
    Immutable configuration for field processing

    Attributes:
        type: Hint for data type inference
        logical_type: Logical type for the field ('never', 'infer', or specific type like 'email')
        nullable: Whether the field can contain null values
        description: Human-readable description
        cast_error: Error handling strategy ('raise', 'coerce', 'ignore')
        leading_zeros: How to handle leading zeros/characters ('never', 'num-auto', 'leading_n')
        na_values: Custom NA values for this field (str, list, or None)
        precision: Decimal precision for numeric fields (int or None)
        datetime_precision: Precision for datetime fields ('s', 'ms', 'us', 'ns')
        datetime_format: Format string for parsing datetime fields ('auto' or strftime format)
        category: Whether this field is categorical (internal use only)
        category_method: Category detection method ('str-auto', 'auto', 'force', 'never')
        properties: Additional field properties
    """

    type: str | None = None
    logical_type: str = "never"
    nullable: bool | None = None
    description: str | None = None
    cast_error: str = "coerce"
    leading_zeros: str = "never"
    na_values: (
        str
        | int
        | float
        | bool
        | datetime
        | list[str | int | float | bool | datetime]
        | None
    ) = None
    precision: int | None = None
    datetime_precision: str = "s"
    datetime_format: str = "auto"
    category: bool = False
    category_method: str = "str-auto"
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.cast_error not in ["raise", "coerce", "ignore"]:
            raise ValueError(f"Invalid cast_error: {self.cast_error}")

        # Validate logical_type parameter
        valid_logical_types = ["never", "infer"]
        if not (
            self.logical_type in valid_logical_types
            or isinstance(self.logical_type, str)
        ):
            raise ValueError(
                "logical_type must be 'never', 'infer', or a specific logical type string"
            )

        # Validate leading_zeros parameter
        valid_leading_zeros = ["never", "num-auto"]
        if not (
            self.leading_zeros in valid_leading_zeros
            or self.leading_zeros.startswith("leading_")
        ):
            raise ValueError(
                f"leading_zeros must be one of {valid_leading_zeros} or 'leading_n' format"
            )

        # Validate category_method parameter
        if self.category_method not in ["str-auto", "auto", "force", "never"]:
            raise ValueError(f"Invalid category_method: {self.category_method}")

        # Validate datetime_precision parameter
        if self.datetime_precision not in ["s", "ms", "us", "ns"]:
            raise ValueError(
                "datetime_precision must be one of ['s', 'ms', 'us', 'ns']"
            )

        # Validate precision parameter
        if self.precision is not None:
            if not isinstance(self.precision, int) or self.precision < 0:
                raise ValueError(
                    f"precision must be a non-negative integer, got: {self.precision}"
                )
            # Check if precision is used with integer types (which is invalid)
            if self.type and self.type.lower() in ["int", "integer"]:
                raise ValueError(
                    f"precision parameter cannot be used with integer types (type: {self.type}). "
                    "precision is only valid for float and decimal types."
                )

        # Validate na_values parameter
        if self.na_values is not None:
            if not isinstance(self.na_values, str | int | float | bool | datetime | list):
                raise ValueError(
                    f"na_values must be str, int, float, bool, datetime, or list, got: {type(self.na_values)}"
                )
            if isinstance(self.na_values, list):
                if not all(
                    isinstance(val, str | int | float | bool | datetime)
                    for val in self.na_values
                ):
                    raise ValueError(
                        "All values in na_values list must be str, int, float, bool, or datetime"
                    )


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
    logical_type: LogicalType | None = None
    nullable: bool = True
    source_dtype: str | None = None
    target_dtype: str | None = None
    description: str | None = None
    cast_error: str = "coerce"
    stats: FieldStats | None = None
    properties: dict[str, Any] = field(default_factory=dict)
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
FieldConfigDict = dict[str, Any]
FieldMetadataDict = dict[str, FieldMetadata]
