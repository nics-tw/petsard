import pandas as pd


def safe_astype(
    data: pd.Series,
    dtype: str,
):
    """
    Safely cast a pandas Series to a given dtype.
    """