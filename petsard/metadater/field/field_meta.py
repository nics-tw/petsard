"""Field-level metadata classes and data structures"""

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import numpy as np

from petsard.metadater.datatype import DataType, LogicalType


@dataclass
class FieldStats:
    """
    Statistics for a single field

    Attr.:
        row_count (int): Total number of rows in the field
        na_count (int): Number of null values
        na_percentage (float): Percentage of null values
        distinct_count (int): Number of distinct values
        min_value (Any): Minimum value in the field
        max_value (Any): Maximum value in the field
        mean_value (Optional[float]): Mean value (if applicable)
        std_value (Optional[float]): Standard deviation (if applicable)
        quantiles (dict[float, Any]): Quantiles of the field values
        most_frequent (Optional[list[tuple[Any, int]]]): Most frequent values and their counts
    """

    row_count: int = 0
    na_count: int = 0
    na_percentage: float = 0.0
    distinct_count: int = 0
    min_value: Any = None
    max_value: Any = None
    mean_value: Optional[float] = None
    std_value: Optional[float] = None
    quantiles: dict[float, Any] = field(default_factory=dict)
    most_frequent: Optional[list[tuple[Any, int]]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        result = asdict(self)
        # Convert numpy types to Python types
        for key, value in result.items():
            if isinstance(value, (np.integer, np.floating)):
                result[key] = value.item()
            elif isinstance(value, np.ndarray):
                result[key] = value.tolist()
        return result


@dataclass
class FieldMetadata:
    """
    Metadata for a single field/column

    Attr.:
        name (str): Name of the field
        data_type (DataType): Data type of the field
        nullable (bool): Whether the field can contain null values
        stats (Optional[FieldStats]): Statistics for the field
        description (Optional[str]): Description of the field
        logical_type (Optional[LogicalType]): Logical type for semantic meaning
        properties (dict[str, Any]): Additional properties for the field
        source_dtype (Optional[str]): Original pandas dtype for type conversion
        target_dtype (Optional[str]): Target dtype for optimization
        cast_error (str): Error handling strategy for type casting
    """

    name: str
    data_type: DataType
    nullable: bool = True
    stats: Optional[FieldStats] = None
    description: Optional[str] = None
    logical_type: Optional[LogicalType] = None
    properties: dict[str, Any] = field(default_factory=dict)

    # Type conversion settings
    source_dtype: Optional[str] = None
    target_dtype: Optional[str] = None
    cast_error: str = "raise"  # 'raise', 'coerce', 'ignore'


@dataclass
class FieldConfig:
    """
    Configuration for a field in the schema

    Attr.:
        type_hint (Optional[str]): Type hint for the field
        cast_error (str): Error handling strategy for type casting
        description (Optional[str]): Description of the field
        logical_type (Optional[str]): Logical type hint
        nullable (Optional[bool]): Whether the field can contain null values
        properties (dict[str, Any]): Additional custom properties
    """

    type_hint: Optional[str] = None
    cast_error: str = "raise"
    description: Optional[str] = None
    logical_type: Optional[str] = None
    nullable: Optional[bool] = None
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration values"""
        valid_cast_errors = {"raise", "coerce", "ignore"}
        if self.cast_error not in valid_cast_errors:
            raise ValueError(
                f"cast_error must be one of {valid_cast_errors}, got '{self.cast_error}'"
            )

        # Validate type_hint if provided
        valid_type_hints = {
            "category",
            "datetime",
            "date",
            "time",
            "int",
            "float",
            "string",
            "boolean",
            "binary",
        }
        if self.type_hint and self.type_hint.lower() not in valid_type_hints:
            import warnings

            warnings.warn(
                f"Unknown type_hint '{self.type_hint}'. "
                f"Standard hints are: {valid_type_hints}"
            )
