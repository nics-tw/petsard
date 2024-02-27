import pandas as pd


def safe_round(value, digits=6):
    """
    Safely rounds a given value to the specified number of digits.

    Args:
        value (float): The value to be rounded.
        digits (int, optional): The number of digits to round to. Defaults to 6.

    Returns:
        float or None: The rounded value, or None if an exception occurs.
    """
    try:
        return round(value, digits)
    except Exception:
        return pd.NA
