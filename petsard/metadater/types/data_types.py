from enum import Enum
from typing import Any


class DataType(Enum):
    """Basic data types for field metadata"""

    BOOLEAN = "boolean"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    DECIMAL = "decimal"
    STRING = "string"
    BINARY = "binary"
    OBJECT = "object"
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    TIMESTAMP_TZ = "timestamp_tz"


class LogicalType(Enum):
    """Logical/semantic types for field metadata

    These types represent semantic meaning beyond basic data types.
    Each logical type has specific data type requirements and validation rules.
    """

    # Text-based semantic types (require string data type)
    EMAIL = "email"  # Email addresses - requires string type
    URL = "url"  # Web URLs - requires string type
    UUID = "uuid"  # UUID identifiers - requires string type
    CATEGORICAL = "categorical"  # Categorical data - requires string type

    # Numeric semantic types
    PERCENTAGE = "percentage"  # Percentage values (0-100) - requires numeric type
    CURRENCY = "currency"  # Monetary values - requires numeric type
    LATITUDE = "latitude"  # Latitude coordinates (-90 to 90) - requires numeric type
    LONGITUDE = (
        "longitude"  # Longitude coordinates (-180 to 180) - requires numeric type
    )

    # Network types (require string data type)
    IP_ADDRESS = "ip_address"  # IP addresses (IPv4/IPv6) - requires string type

    # Identifier types
    PRIMARY_KEY = "primary_key"  # Primary key fields - requires uniqueness validation


# Logical type to compatible data types mapping
LOGICAL_TYPE_COMPATIBLE_DATA_TYPES = {
    # Text-based semantic types - require string data type
    LogicalType.EMAIL: [DataType.STRING],
    LogicalType.URL: [DataType.STRING],
    LogicalType.UUID: [DataType.STRING],
    LogicalType.CATEGORICAL: [DataType.STRING],
    LogicalType.IP_ADDRESS: [DataType.STRING],
    # Numeric semantic types - require numeric data types
    LogicalType.PERCENTAGE: [
        DataType.INT8,
        DataType.INT16,
        DataType.INT32,
        DataType.INT64,
        DataType.FLOAT32,
        DataType.FLOAT64,
        DataType.DECIMAL,
    ],
    LogicalType.CURRENCY: [DataType.FLOAT32, DataType.FLOAT64, DataType.DECIMAL],
    LogicalType.LATITUDE: [DataType.FLOAT32, DataType.FLOAT64, DataType.DECIMAL],
    LogicalType.LONGITUDE: [DataType.FLOAT32, DataType.FLOAT64, DataType.DECIMAL],
    # Identifier types - can be various types depending on implementation
    LogicalType.PRIMARY_KEY: [
        DataType.INT8,
        DataType.INT16,
        DataType.INT32,
        DataType.INT64,
        DataType.STRING,
    ],
}


def validate_logical_type_compatibility(
    logical_type: LogicalType, data_type: DataType
) -> bool:
    """
    Validate if a logical type is compatible with a data type

    Args:
        logical_type: The logical type to validate
        data_type: The data type to check compatibility with

    Returns:
        bool: True if compatible, False otherwise
    """
    if logical_type not in LOGICAL_TYPE_COMPATIBLE_DATA_TYPES:
        return False

    compatible_types = LOGICAL_TYPE_COMPATIBLE_DATA_TYPES[logical_type]
    return data_type in compatible_types


def get_logical_type_requirements(logical_type: LogicalType) -> dict[str, Any]:
    """
    Get the requirements and validation rules for a logical type

    Args:
        logical_type: The logical type to get requirements for

    Returns:
        dict: Requirements including compatible data types, validation rules, etc.
    """
    requirements = {
        LogicalType.EMAIL: {
            "compatible_data_types": [DataType.STRING],
            "validation_pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "confidence_threshold": 0.8,
            "description": "Email addresses with standard format validation",
        },
        LogicalType.URL: {
            "compatible_data_types": [DataType.STRING],
            "validation_pattern": r"^https?://[^\s/$.?#].[^\s]*$",
            "confidence_threshold": 0.8,
            "description": "Web URLs with protocol validation",
        },
        LogicalType.UUID: {
            "compatible_data_types": [DataType.STRING],
            "validation_pattern": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
            "confidence_threshold": 0.95,
            "description": "UUID identifiers in standard format",
        },
        LogicalType.CATEGORICAL: {
            "compatible_data_types": [DataType.STRING],
            "validation_method": "cardinality_analysis",
            "confidence_threshold": "dynamic",
            "description": "Categorical data detected via ASPL cardinality analysis",
        },
        LogicalType.IP_ADDRESS: {
            "compatible_data_types": [DataType.STRING],
            "validation_pattern": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
            "confidence_threshold": 0.9,
            "description": "IPv4 and IPv6 addresses",
        },
        LogicalType.PERCENTAGE: {
            "compatible_data_types": [
                DataType.INT8,
                DataType.INT16,
                DataType.INT32,
                DataType.INT64,
                DataType.FLOAT32,
                DataType.FLOAT64,
                DataType.DECIMAL,
            ],
            "validation_range": (0, 100),
            "confidence_threshold": 0.95,
            "description": "Percentage values in 0-100 range",
        },
        LogicalType.CURRENCY: {
            "compatible_data_types": [
                DataType.FLOAT32,
                DataType.FLOAT64,
                DataType.DECIMAL,
            ],
            "validation_method": "currency_symbol_detection",
            "confidence_threshold": 0.8,
            "description": "Monetary values with currency symbol detection",
        },
        LogicalType.LATITUDE: {
            "compatible_data_types": [
                DataType.FLOAT32,
                DataType.FLOAT64,
                DataType.DECIMAL,
            ],
            "validation_range": (-90, 90),
            "confidence_threshold": 0.95,
            "description": "Latitude coordinates in -90 to 90 range",
        },
        LogicalType.LONGITUDE: {
            "compatible_data_types": [
                DataType.FLOAT32,
                DataType.FLOAT64,
                DataType.DECIMAL,
            ],
            "validation_range": (-180, 180),
            "confidence_threshold": 0.95,
            "description": "Longitude coordinates in -180 to 180 range",
        },
        LogicalType.PRIMARY_KEY: {
            "compatible_data_types": [
                DataType.INT8,
                DataType.INT16,
                DataType.INT32,
                DataType.INT64,
                DataType.STRING,
            ],
            "validation_method": "uniqueness_check",
            "confidence_threshold": 1.0,  # Must be 100% unique
            "description": "Primary key fields with uniqueness validation",
        },
    }

    return requirements.get(logical_type, {})


def safe_round(value: Any, decimals: int = 2) -> int | float | None:
    """
    安全的四捨五入函數，處理 None 和非數值類型

    Args:
        value: 要四捨五入的值
        decimals: 小數位數

    Returns:
        四捨五入後的值，如果輸入無效則返回 None
    """
    if value is None:
        return None

    try:
        if isinstance(value, int | float):
            rounded = round(float(value), decimals)
            # 如果小數位數為 0 且結果是整數，返回 int
            if decimals == 0:
                return int(rounded)
            return rounded
        else:
            # 處理 pandas Series 的情況
            import pandas as pd

            if isinstance(value, pd.Series):
                if len(value) == 1:
                    # 使用 .iloc[0] 來避免 FutureWarning
                    numeric_value = float(value.iloc[0])
                else:
                    # 多元素 Series 無法轉換為單一數值
                    return None
            else:
                # 嘗試轉換為數值
                numeric_value = float(value)

            rounded = round(numeric_value, decimals)
            if decimals == 0:
                return int(rounded)
            return rounded
    except (ValueError, TypeError, OverflowError):
        return None


# 評估分數粒度對應表
EvaluationScoreGranularityMap = {
    "high": 0.01,
    "medium": 0.1,
    "low": 1.0,
}


# Type aliases
DataTypeValue = DataType | str
LogicalTypeValue = LogicalType | str
