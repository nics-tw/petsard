from dateutil.parser import parse
import numpy as np
import pandas as pd
from pandas.api.types import (
    is_string_dtype,
    is_numeric_dtype,
    is_integer_dtype,
    is_float_dtype
)


def df_cast_check(
    df_data:    pd.DataFrame,
    dict_dtype: dict = None
) -> dict:
    """
    Function for Check each column best dtypes
        with its mininum stroage of pd.DataFrame

    - For Data of 'Object' Type:
        - Categorize as 'categorical'
            if the majority of the data cannot be recognized as a date,
            specifically when the count of non-date entries
            is greater than or equal to
            the maximum count of either date or datetime entries.
        - Otherwise, categorize as 'datetime'
            if any time information is included
        - In all other cases, categorize as 'date'.

        20231103, Justyn:
            pandas didn't suppot float16 engine,
            and some of library will try to handle your column as index
            (e.g. SDV, Gaussian Coupula)
            then it will cause Error:
            "NotImplementedError: float16 indexes are not supported"
            Therefore I decide to set a min of float as float32.
    """

    def _col_cast_check_string(col_data: pd.Series) -> str:
        cnt_date, cnt_datetime, cnt_category = 0, 0, 0
        for value in col_data.dropna():
            try:
                parsed_col_data = parse(value)
                if parsed_col_data.hour == 0\
                        and parsed_col_data.minute == 0\
                        and parsed_col_data.second == 0:
                    cnt_datetime += 1
                else:
                    cnt_date += 1
            # TODO Error assignment
            #     I notices we should assign value via Error,
            #     but have no idea how to avoid it here
            except (ValueError, TypeError):
                cnt_category += 1

        if cnt_category >= max(cnt_date, cnt_datetime):
            return 'category'
        elif cnt_datetime >= 1:
            return 'datetime'
        else:
            return 'date'

    def _col_cast_check_numeric(
        col_data: pd.Series,
        force_type: str = ''
    ) -> str:

        type_int_ranges = {
            'int8': (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
            'int16': (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
            'int32': (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
            'int64': (np.iinfo(np.int64).min, np.iinfo(np.int64).max)
        }
        type_float_ranges = {
            'float32': (np.finfo(np.float32).min, np.finfo(np.float32).max),
            'float64': (np.finfo(np.float64).min, np.finfo(np.float64).max)
        }

        col_min = 0.0 if np.all(np.isnan(col_data)) else np.nanmin(col_data)
        col_max = 0.0 if np.all(np.isnan(col_data)) else np.nanmax(col_data)
        if is_integer_dtype(col_data) or force_type.startswith('int'):
            for dtype, (min, max) in type_int_ranges.items():
                if min < col_min <= col_max < max:
                    return dtype
        elif is_float_dtype(col_data) or force_type.startswith('float'):
            for dtype, (min, max) in type_float_ranges.items():
                if min < col_min <= col_max < max:
                    return dtype
        else:
            # already is_numeric_dtype(col_data)
            return 'numeric-other'

    def _col_cast_check(col_data: pd.Series) -> str:
        if is_string_dtype(col_data):
            return _col_cast_check_string(col_data)
        elif is_numeric_dtype(col_data):
            return _col_cast_check_numeric(col_data)
        else:
            return 'error'

    if not dict_dtype:
        dict_dtype = {}

    for col_name, col_data in df_data.items():
        col_data.dropna(inplace=True)
        if col_name in dict_dtype:
            # print(f"{col_name} as {str(dict_dtype[col_name])}")
            # Forced change float16 to float32
            if dict_dtype[col_name].lower() == 'float16':
                dict_dtype[col_name] = 'float32'
                print(
                    f"Util - df_cast_check: The dtype for '{col_name}' "
                    f"has been changed from 'float16' to 'float32' "
                    "due to compatibility issues."
                )

            force_type = dict_dtype[col_name].lower()

            # Special handle if already been defined.
            if force_type in ['category', 'date', 'datetime']:
                dict_dtype[col_name] = force_type
            elif force_type in ['int', 'float']:
                # If only defined int/float but no digits.
                dict_dtype[col_name] = _col_cast_check_numeric(
                    col_data,
                    force_type
                )
            elif force_type.startswith('int') or \
                    force_type.startswith('float'):
                dict_dtype[col_name] = force_type
            else:
                # TODO Error.py
                raise ValueError('\n'.join([
                    f"Util - df_cast_check: "
                    f"Unsupported force dtype, "
                    f"now is {force_type}.",
                    f"We only support "
                    f"category/date/datetime/int-/float-."
                ]))
        else:
            # Otherwise determine by extreme value.
            dict_dtype[col_name] = _col_cast_check(col_data)

    return dict_dtype
