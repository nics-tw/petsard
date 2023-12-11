
def df_cast_check(df_data    # : pd.DataFrame
                 ,dict_dtype   : dict         = None
                 ) -> dict:
    """
    Function for Check each column best dtypes with its mininum stroage of pd.DataFrame

    - For Data of 'Object' Type:
        - Categorize as 'categorical' if the majority of the data cannot be recognized as a date, specifically when the count of non-date entries is greater than or equal to the maximum count of either date or datetime entries.
        - Otherwise, categorize as 'datetime' if any time information is included
        - In all other cases, categorize as 'date'.
    
    20231103, Justyn:
        pandas didn't suppot float16 engine,
        and some of library will try to handle your column as index (e.g. SDV, Gaussian Coupula)
        then it will cause Error: "NotImplementedError: float16 indexes are not supported"
        Therefore I decide to set a min of float as float32.
    """
    def __col_cast_check_string(col_data # : pd.Series
                               ) -> str:
        from dateutil.parser import parse
        _cnt_date ,_cnt_datetime ,_cnt_category = 0,0,0
        for _value in col_data.dropna():
            try:
                _parsed_col_data = parse(_value)
                if  _parsed_col_data.hour   == 0\
                and _parsed_col_data.minute == 0\
                and _parsed_col_data.second == 0:
                    _cnt_datetime += 1
                else:
                    _cnt_date += 1 
            except (ValueError, TypeError):
                _cnt_category += 1
            
        if _cnt_category >= max(_cnt_date, _cnt_datetime):
            return 'category'
        elif _cnt_datetime >= 1:
            return 'datetime'
        else:
            return 'date'




    def __col_cast_check_numeric(col_data  # : pd.Series
                                ,force_type  : str = None
                                ) -> str:
        from pandas.api.types import is_integer_dtype ,is_float_dtype
        import numpy as np

        _type_int_ranges = {
            'int8'  : (np.iinfo(np.int8 ).min ,np.iinfo(np.int8 ).max)
           ,'int16' : (np.iinfo(np.int16).min ,np.iinfo(np.int16).max)
           ,'int32' : (np.iinfo(np.int32).min ,np.iinfo(np.int32).max)
           ,'int64' : (np.iinfo(np.int64).min ,np.iinfo(np.int64).max)
        }
        _type_float_ranges = {
            'float32': (np.finfo(np.float32).min ,np.finfo(np.float32).max)
           ,'float64': (np.finfo(np.float64).min ,np.finfo(np.float64).max)
        }

        _col_min = 0.0 if np.all(np.isnan(col_data)) else np.nanmin(col_data)
        _col_max = 0.0 if np.all(np.isnan(col_data)) else np.nanmax(col_data)
        if   is_integer_dtype(col_data) or force_type.startswith('int'):
            for _dtype, (_min ,_max) in _type_int_ranges.items():
                if _min < _col_min <= _col_max < _max:
                    return _dtype
        elif is_float_dtype(col_data) or force_type.startswith('float'):
            for _dtype, (_min ,_max) in _type_float_ranges.items():
                if _min < _col_min <= _col_max < _max:
                    return _dtype
        else:
            return 'numeric-other' # already is_numeric_dtype(col_data)



    def __col_cast_check(col_data # : pd.Series
                        ) -> str:
        from pandas.api.types import is_string_dtype ,is_numeric_dtype
        if is_string_dtype(col_data):
            return __col_cast_check_string( col_data)
        elif is_numeric_dtype(col_data):
            return __col_cast_check_numeric(col_data)
        else:
            return 'error'



    if not dict_dtype:
        dict_dtype = {}

    for _col_name, _col_data in df_data.items():
        _col_data.dropna(inplace=True)
        if _col_name in dict_dtype:
            print(f"{_col_name} as {str(dict_dtype[_col_name])}")
            ####### ####### ####### ####### ####### ######
            ####### Change float16 to float32
            if dict_dtype[_col_name].lower() == 'float16':
                dict_dtype[_col_name] = 'float32'
                print(f"Notice: The dtype for '{_col_name}' has been changed from 'float16' to 'float32' due to compatibility issues.")

            _force_type = dict_dtype[_col_name].lower()

            ####### ####### ####### ####### ####### ######
            ####### Special handle if already been defined.
            if _force_type in ['category' ,'date' ,'datetime']:
                dict_dtype[_col_name] = _force_type
            elif _force_type in ['int' ,'float']:
                ####### ####### ####### ####### ####### ######
                ####### If only defined int/float but no digits.
                dict_dtype[_col_name] = __col_cast_check_numeric(_col_data ,_force_type)
            elif _force_type.startswith('int') or _force_type.startswith('float'):
                dict_dtype[_col_name] = _force_type
            else:
                raise ValueError('\n'.join([f"Unsupported force dtype, now is {_force_type}."
                                           ,f"We only support category/date/datetime/int-/float-."
                                           ]))
        else:
            ####### ####### ####### ####### ####### ######
            ####### Otherwise determine by extreme value.
            dict_dtype[_col_name] = __col_cast_check(_col_data)

    return dict_dtype