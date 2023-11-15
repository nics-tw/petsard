####### ####### ####### ####### ####### ######
# Downcast in pandas df                      #
####### ####### ####### ####### ####### ######
# [TODO] add determine of date
# [TODO] avoid already have a category as ''
def df_downcast(df):
    import numpy  as np
    import pandas as pd
    list_col       = df.dtypes.index.tolist()
    list_col_dtype = df.dtypes.values.tolist()
    for idx ,col_dtype in enumerate(list_col_dtype):
        col_name  = list_col[idx]
        col_dtype = str(col_dtype)
        if   col_dtype == 'object':
            if col_name == 'date':
                df[col_name] = pd.to_datetime(df[col_name], format='%Y-%m-%d')
            else:
                df[col_name] = df[col_name].fillna('').astype('category')
        elif 'int' in col_dtype or 'float' in col_dtype:
            col_min = df[col_name].min()
            col_max = df[col_name].max()
            if   'int' in col_dtype:
                if   col_min > np.iinfo(np.int8 ).min and col_max < np.iinfo(np.int8 ).max:
                    df[col_name] = df[col_name].astype(np.int8 )
                elif col_min > np.iinfo(np.int16).min and col_max < np.iinfo(np.int16).max:
                    df[col_name] = df[col_name].astype(np.int16)
                elif col_min > np.iinfo(np.int32).min and col_max < np.iinfo(np.int32).max:
                    df[col_name] = df[col_name].astype(np.int32)
                else:
                    df[col_name] = df[col_name].astype(np.int64)
            elif 'float' in col_dtype:
                # 20231103, Justyn: pandas didn't suppot float16 engine, and some of library will try to handle your column as index (e.g. SDV, Gaussian Coupula)
                #                   then it will cause Error: "NotImplementedError: float16 indexes are not supported"
                #                   I decide to set a min of float as float32
                if   col_min > np.finfo(np.float32).min and col_max < np.finfo(np.float32).max:
                    df[col_name] = df[col_name].astype(np.float32)
                else:
                    df[col_name] = df[col_name].astype(np.float64)
    return df



####### ####### ####### ####### ####### ######
# Update Nested dict                         #
####### ####### ####### ####### ####### ######
def update_append_nested(default ,update):
    for key ,value in update.items():
        if key in default:
            if isinstance(value ,dict) and isinstance(default[key] ,dict):
                update_append_nested(default[key] ,value)
            else:
                default[key] = value
        else:
            default[key] = value
    return default


