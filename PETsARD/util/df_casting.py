####### ####### ####### ####### ####### ######
# Downcast in pandas df                      #
####### ####### ####### ####### ####### ######
# [TODO] avoid already have a category as ''
def df_casting(df_data  # : pd.DataFrame
              ,dict_dtype : dict         = None
              ): # -> pd.DataFrame
    """
    Function for down-casting each columns of pd.DataFrame
    """
    ####### ####### ####### ####### ####### ######
    ####### Check the optimized dtype
    if not dict_dtype:
        dict_dtype = {}
    from . import df_cast_check
    dict_dtype.update(df_cast_check(df_data ,dict_dtype))

    import numpy as np
    _type_numeric = {
         'int8'   : np.int8
        ,'int16'  : np.int16
        ,'int32'  : np.int32
        ,'int64'  : np.int64
        ,'float32': np.float32
        ,'float64': np.float64
    }
    for _col_name, _col_data in df_data.items():
        if _col_name in dict_dtype:
            _col_dtype_new = dict_dtype[_col_name]
            ####### ####### ####### ####### ####### ######
            ####### Category
            if   _col_dtype_new == 'category':
                df_data[_col_name] = _col_data.astype(_col_dtype_new)
            ####### ####### ####### ####### ####### ######
            ####### Date/Datetime
            elif _col_dtype_new == 'date':
                df_data[_col_name] = pd.to_datetime(_col_data , errors='coerce').dt.date
            elif _col_dtype_new == 'datetime':
                df_data[_col_name] = pd.to_datetime(_col_data , errors='coerce')
            ####### ####### ####### ####### ####### ######
            ####### Numeric
            elif _col_dtype_new.startswith('int'  )\
              or _col_dtype_new.startswith('float'):
                df_data[_col_name] = _col_data.astype(_type_numeric[_col_dtype_new])
    return df_data

