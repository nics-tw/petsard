import numpy as np
import pandas as pd

from PETsARD.util import df_cast_check


def df_casting(
    df_data: pd.DataFrame,
    dict_dtype: dict = None
) -> pd.DataFrame:
    """
    Function for down-casting each columns of pd.DataFrame

    TODO avoid already have a category as ''
        But maybe this issue should handle by loader
    """
    # Check the optimized dtype
    if not dict_dtype:
        dict_dtype = {}
    dict_dtype.update(df_cast_check(df_data, dict_dtype))

    type_numeric = {
        'int8': np.int8,
        'int16': np.int16,
        'int32': np.int32,
        'int64': np.int64,
        'float32': np.float32,
        'float64': np.float64
    }
    for col_name, col_data in df_data.items():
        if col_name in dict_dtype:
            col_dtype_new = dict_dtype[col_name]
            # Category
            if col_dtype_new == 'category':
                df_data[col_name] = col_data.astype(col_dtype_new)
            # Date/Datetime
            elif col_dtype_new == 'date':
                df_data[col_name] = pd.to_datetime(
                    col_data,
                    errors='coerce'
                ).dt.date
            elif col_dtype_new == 'datetime':
                df_data[col_name] = pd.to_datetime(
                    col_data,
                    errors='coerce'
                )
            # Numeric
            elif col_dtype_new.startswith('int') or \
                    col_dtype_new.startswith('float'):
                df_data[col_name] = col_data.astype(
                    type_numeric[col_dtype_new])
    return df_data
