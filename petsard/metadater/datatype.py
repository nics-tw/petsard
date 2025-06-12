from enum import Enum


class DataType(Enum):
    """
    Standard data types for metadata system

    Attr.:
        BOOLEAN (str): Boolean type
        INT8 (str): 8-bit integer
        INT16 (str): 16-bit integer
        INT32 (str): 32-bit integer
        INT64 (str): 64-bit integer
        FLOAT32 (str): 32-bit floating point
        FLOAT64 (str): 64-bit floating point
        DECIMAL (str): Decimal type
        STRING (str): String type
        BINARY (str): Binary type
        DATE (str): Date type
        TIME (str): Time type
        TIMESTAMP (str): Timestamp type
        TIMESTAMP_TZ (str): Timestamp with timezone type
        UUID (str): UUID type
        FIXED (str): Fixed-length byte array type
    """

    # Primitive types
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

    # Date/Time types
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    TIMESTAMP_TZ = "timestamp_tz"

    # Special types
    UUID = "uuid"  # Universally Unique Identifier
    FIXED = "fixed"  # Fixed-length byte array


class LogicalType(Enum):
    """
    Logical types that provide semantic meaning

    Attr.:
        EMAIL (str): Email address
        URL (str): URL
        JSON (str): JSON object
        PHONE (str): Phone number
        CURRENCY (str): Currency value
        PERCENTAGE (str): Percentage value
        CATEGORICAL (str): Categorical data
        ORDINAL (str): Ordinal data
        LATITUDE (str): Latitude coordinate
        LONGITUDE (str): Longitude coordinate
        EMBEDDING (str): Vector embedding
        IP_ADDRESS (str): IP address (IPv4)
        IPV6_ADDRESS (str): IPv6 address
        MAC_ADDRESS (str): MAC address
        UUID (str): UUID
        CREDIT_CARD (str): Credit card number (masked detection only)
        POSTAL_CODE (str): Postal/ZIP code
        COLOR_HEX (str): Hexadecimal color code
        HASH_MD5 (str): MD5 hash
        HASH_SHA256 (str): SHA256 hash
        FILE_PATH (str): File system path
        DATETIME_ISO (str): ISO 8601 datetime string
    """

    EMAIL = "email"
    URL = "url"
    JSON = "json"
    PHONE = "phone"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    EMBEDDING = "embedding"
    IP_ADDRESS = "ip_address"
    IPV6_ADDRESS = "ipv6_address"
    MAC_ADDRESS = "mac_address"
    UUID = "uuid"
    CREDIT_CARD = "credit_card"
    POSTAL_CODE = "postal_code"
    COLOR_HEX = "color_hex"
    HASH_MD5 = "hash_md5"
    HASH_SHA256 = "hash_sha256"
    FILE_PATH = "file_path"
    DATETIME_ISO = "datetime_iso"


def legacy_safe_round(value: float, decimals: int = 4) -> float:
    """Safe round function"""
    return round(value, decimals)
