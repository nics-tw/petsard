import pandas as pd

from petsard.exceptions import ConfigError
from petsard.util.params import OPTIMIZED_DTYPES


def casting_dataframe(data: pd.DataFrame, optimized_dtypes: dict) -> pd.DataFrame:
    """
    Casts the columns of a DataFrame to their optimized data types.

    Args:
        data (pd.DataFrame): The DataFrame to be casted.
        optimized_dtypes (dict): A dictionary mapping column names to their optimized data types.

    Returns:
        pd.DataFrame: The DataFrame with columns casted to their optimized data types.
    """
    for col_name in data.columns:
        optimized_dtype: str = optimized_dtypes.get(col_name, None)

        if optimized_dtype is None:
            raise ConfigError
        elif optimized_dtype == "datetime":
            optimized_dtype = OPTIMIZED_DTYPES["datetime"]

        try:
            data[col_name] = data[col_name].astype(optimized_dtype)
        except Exception:
            data[col_name] = data[col_name].astype("object")

    return data
