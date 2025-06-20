"""Core data type definitions and utilities"""

from enum import Enum
from typing import Any, Optional, Union


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
    """Logical/semantic types for field metadata"""

    # Numeric types
    INTEGER = "integer"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"

    # Text types
    TEXT = "text"
    CATEGORICAL = "categorical"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"

    # Geographic types
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    IP_ADDRESS = "ip_address"

    # Temporal types
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    DURATION = "duration"

    # Identifiers
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"


def safe_round(value: Any, decimals: int = 2) -> Optional[Union[int, float]]:
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
        if isinstance(value, (int, float)):
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
DataTypeValue = Union[DataType, str]
LogicalTypeValue = Union[LogicalType, str]
