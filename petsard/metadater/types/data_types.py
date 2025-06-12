"""Basic data type definitions for the metadater module"""

from enum import Enum
from typing import Any, Union


class DataType(Enum):
    """Basic data types supported by the metadater"""

    # Numeric types
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    DECIMAL = "decimal"

    # Text types
    STRING = "string"
    BINARY = "binary"

    # Boolean type
    BOOLEAN = "boolean"

    # Date/Time types
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    TIMESTAMP_TZ = "timestamp_tz"

    # Complex types
    JSON = "json"
    ARRAY = "array"
    OBJECT = "object"

    # Unknown type
    UNKNOWN = "unknown"


class LogicalType(Enum):
    """Logical types that provide semantic meaning to data"""

    # Identifiers
    UUID = "uuid"
    ID = "id"

    # Contact information
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"

    # Geographic
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    IP_ADDRESS = "ip_address"
    POSTAL_CODE = "postal_code"
    COUNTRY_CODE = "country_code"

    # Financial
    CURRENCY = "currency"
    PERCENTAGE = "percentage"

    # Categorical
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"

    # Text patterns
    REGEX_PATTERN = "regex_pattern"

    # Other
    HASH = "hash"
    ENCODED = "encoded"


# Type aliases for better readability
DataTypeValue = Union[DataType, str]
LogicalTypeValue = Union[LogicalType, str, None]
AnyValue = Any


def safe_round(value: float, decimals: int = 4) -> float:
    """
    Safely round a float value to specified decimal places.

    This is a legacy compatibility function.

    Args:
        value: The value to round
        decimals: Number of decimal places

    Returns:
        Rounded value
    """
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return 0.0


# Legacy compatibility
legacy_safe_round = safe_round
