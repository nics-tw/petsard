import hashlib
from typing import Dict

import pandas as pd

from PETsARD.error import ConfigError
from PETsARD.util import OPTIMIZED_DTYPES

def DigestSha256(filepath):
    """
    Calculate SHA-256 value of file. Load 128KB at one time.
    ...
    Args:
        filepath (str) Openable file full path.
    ...
    return:
        (str) SHA-256 value of file.
    """
    sha256hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(131072), b""):
            sha256hash.update(byte_block)
    return sha256hash.hexdigest()


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
        elif optimized_dtype == 'datetime':
            optimized_dtype = OPTIMIZED_DTYPES['datetime']

        data[col_name] = data[col_name].astype(optimized_dtype)

    return data
