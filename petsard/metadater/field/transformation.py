"""Pure functions for data transformation operations"""

import pandas as pd

from petsard.metadater.field.field_types import FieldMetadata
from petsard.metadater.types.data_types import DataType, LogicalType


def transform_field_data(
    field_data: pd.Series,
    field_metadata: FieldMetadata,
) -> pd.Series:
    """
    Pure function to transform field data based on metadata

    Args:
        field_data: Series to transform
        field_metadata: Metadata with transformation rules

    Returns:
        Transformed series
    """
    result = field_data.copy()

    # Apply dtype conversion if target dtype is specified
    if field_metadata.target_dtype and field_metadata.target_dtype != str(
        field_data.dtype
    ):
        result = apply_dtype_conversion(
            field_data=result,
            target_dtype=field_metadata.target_dtype,
            cast_error=field_metadata.cast_error,
        )

    # Apply logical type transformation
    if field_metadata.logical_type:
        result = apply_logical_type_transformation(
            field_data=result,
            logical_type=field_metadata.logical_type,
        )

    # Handle nullability
    if not field_metadata.nullable and result.isna().any():
        if field_metadata.cast_error == "raise":
            raise ValueError(
                f"Field '{field_metadata.name}' contains null values but nullable=False"
            )
        elif field_metadata.cast_error == "coerce":
            result = fill_nulls(result, field_metadata)

    return result


def apply_dtype_conversion(
    field_data: pd.Series,
    target_dtype: str,
    cast_error: str = "coerce",
) -> pd.Series:
    """
    Pure function to apply dtype conversion with error handling

    Args:
        field_data: Series to convert
        target_dtype: Target data type
        cast_error: Error handling strategy ('raise', 'coerce', 'ignore')

    Returns:
        Converted series
    """
    if cast_error == "ignore":
        return field_data

    try:
        # Special handling for different dtype categories
        if target_dtype == "category":
            return field_data.astype("category")

        elif "datetime" in target_dtype:
            if cast_error == "coerce":
                return pd.to_datetime(field_data, errors="coerce")
            else:
                return pd.to_datetime(field_data)

        elif target_dtype in ["int8", "int16", "int32", "int64"]:
            if cast_error == "coerce":
                # First convert to numeric, then to specific int type
                numeric_data = pd.to_numeric(field_data, errors="coerce")
                # Handle NaN values for integer conversion
                if numeric_data.isna().any():
                    # Use nullable integer type
                    nullable_dtype = target_dtype.capitalize()
                    return numeric_data.astype(nullable_dtype)
                else:
                    return numeric_data.astype(target_dtype)
            else:
                return field_data.astype(target_dtype)

        elif target_dtype in ["float16", "float32", "float64"]:
            if cast_error == "coerce":
                numeric_data = pd.to_numeric(field_data, errors="coerce")
                return numeric_data.astype(target_dtype)
            else:
                return field_data.astype(target_dtype)

        elif target_dtype == "string":
            # Use pandas string dtype
            if cast_error == "coerce":
                # Convert to string, handling any type
                return field_data.astype(str).astype("string")
            else:
                return field_data.astype("string")

        elif target_dtype == "boolean":
            if cast_error == "coerce":
                # Custom boolean conversion
                return coerce_to_boolean(field_data)
            else:
                return field_data.astype("boolean")

        else:
            # Generic conversion
            if cast_error == "coerce":
                try:
                    return field_data.astype(target_dtype)
                except Exception:
                    return field_data
            else:
                return field_data.astype(target_dtype)

    except Exception:
        if cast_error == "raise":
            raise
        elif cast_error == "coerce":
            return field_data
        else:  # ignore
            return field_data


def apply_logical_type_transformation(
    field_data: pd.Series,
    logical_type: LogicalType,
) -> pd.Series:
    """
    Pure function to apply transformations based on logical type

    Args:
        field_data: Series to transform
        logical_type: Logical type to apply

    Returns:
        Transformed series
    """
    # Define transformation mappings
    transformations = {
        LogicalType.EMAIL: lambda s: s.str.lower().str.strip(),
        LogicalType.URL: lambda s: s.str.strip(),
        LogicalType.PHONE: lambda s: s.str.replace(r"[^\d+]", "", regex=True),
        LogicalType.CATEGORICAL: lambda s: s.astype("category"),
        LogicalType.CURRENCY: lambda s: clean_currency(s),
        LogicalType.PERCENTAGE: lambda s: clean_percentage(s),
        LogicalType.POSTAL_CODE: lambda s: s.str.upper().str.strip(),
        LogicalType.UUID: lambda s: s.str.lower().str.strip(),
    }

    # Apply transformation if available
    if logical_type in transformations:
        try:
            return transformations[logical_type](field_data)
        except Exception:
            # Return original data if transformation fails
            pass

    return field_data


def fill_nulls(field_data: pd.Series, field_metadata: FieldMetadata) -> pd.Series:
    """
    Pure function to fill null values based on field metadata

    Args:
        field_data: Series with nulls to fill
        field_metadata: Field metadata for context

    Returns:
        Series with filled nulls
    """
    # Determine fill value based on data type
    if field_metadata.data_type in [
        DataType.INT8,
        DataType.INT16,
        DataType.INT32,
        DataType.INT64,
    ]:
        fill_value = 0
    elif field_metadata.data_type in [DataType.FLOAT32, DataType.FLOAT64]:
        fill_value = 0.0
    elif field_metadata.data_type == DataType.BOOLEAN:
        fill_value = False
    elif field_metadata.data_type == DataType.STRING:
        fill_value = ""
    elif field_metadata.data_type in [
        DataType.DATE,
        DataType.TIMESTAMP,
        DataType.TIMESTAMP_TZ,
    ]:
        fill_value = pd.NaT
    else:
        # For other types, forward fill then backward fill
        return field_data.ffill().bfill()

    return field_data.fillna(fill_value)


def coerce_to_boolean(field_data: pd.Series) -> pd.Series:
    """
    Pure function to coerce series to boolean with flexible conversion

    Args:
        field_data: Series to convert

    Returns:
        Boolean series
    """
    # Define truth values
    true_values = {"true", "t", "yes", "y", "1", "on", "enabled"}
    false_values = {"false", "f", "no", "n", "0", "off", "disabled"}

    # Convert to string and lowercase for comparison
    str_series = field_data.astype(str).str.lower().str.strip()

    # Create boolean series
    result = pd.Series(index=field_data.index, dtype="boolean")
    result[str_series.isin(true_values)] = True
    result[str_series.isin(false_values)] = False
    # Keep original NaN values
    result[field_data.isna()] = pd.NA

    return result


def clean_currency(field_data: pd.Series) -> pd.Series:
    """
    Pure function to clean currency values to numeric

    Args:
        field_data: Series with currency values

    Returns:
        Numeric series
    """
    # Remove currency symbols and commas
    cleaned = field_data.astype(str).str.replace(r"[$€£¥,]", "", regex=True)
    # Convert to numeric
    return pd.to_numeric(cleaned, errors="coerce")


def clean_percentage(field_data: pd.Series) -> pd.Series:
    """
    Pure function to clean percentage values to numeric (0-1 scale)

    Args:
        field_data: Series with percentage values

    Returns:
        Numeric series (0-1 scale)
    """
    # Remove percentage sign
    cleaned = field_data.astype(str).str.replace("%", "", regex=False)
    # Convert to numeric and divide by 100
    numeric = pd.to_numeric(cleaned, errors="coerce")

    # If values are already between 0 and 1, assume they're already in decimal form
    if (numeric <= 1).all():
        return numeric
    else:
        return numeric / 100


def normalize_text(field_data: pd.Series, method: str = "lower") -> pd.Series:
    """
    Pure function to normalize text data

    Args:
        field_data: Series with text data
        method: Normalization method ('lower', 'upper', 'title', 'strip')

    Returns:
        Normalized text series
    """
    if method == "lower":
        return field_data.str.lower()
    elif method == "upper":
        return field_data.str.upper()
    elif method == "title":
        return field_data.str.title()
    elif method == "strip":
        return field_data.str.strip()
    else:
        return field_data


def standardize_phone_numbers(field_data: pd.Series) -> pd.Series:
    """
    Pure function to standardize phone numbers

    Args:
        field_data: Series with phone numbers

    Returns:
        Standardized phone number series
    """
    # Remove all non-digit characters except +
    cleaned = field_data.str.replace(r"[^\d+]", "", regex=True)
    return cleaned


def validate_and_clean_emails(field_data: pd.Series) -> pd.Series:
    """
    Pure function to validate and clean email addresses

    Args:
        field_data: Series with email addresses

    Returns:
        Cleaned email series (invalid emails become NaN)
    """
    # Basic email pattern
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    # Clean emails (lowercase and strip)
    cleaned = field_data.str.lower().str.strip()

    # Validate and set invalid emails to NaN
    valid_mask = cleaned.str.match(email_pattern, na=False)
    result = cleaned.copy()
    result[~valid_mask] = pd.NA

    return result
