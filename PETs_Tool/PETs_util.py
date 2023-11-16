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
# label_encoding                             #
####### ####### ####### ####### ####### ######
def label_encoding(df_data):
    from pandas import factorize
    for col in df_data.select_dtypes(['category' ,'object']).columns:
        if   df_data[col].dtype == 'category':
            df_data[col] = df_data[col].cat.codes
        elif df_data[col].dtype == 'object':
            df_data[col], _ = factorize(df_data[col])
    return df_data



####### ####### ####### ####### ####### ######
# Split pandas by P % for N times (sample with replacement) #
####### ####### ####### ####### ####### ######
def df_sample(df_data
             ,sample_ratio=0.8
             ,random_state=None):
    __idx_train = df_data.sample(frac         = sample_ratio
                                ,random_state = random_state).index
    __idx_validation = df_data.drop(__idx_train).index

    __df_train      = df_data.loc[__idx_train     ].reset_index(drop=True)
    __df_validation = df_data.loc[__idx_validation].reset_index(drop=True)
    return __df_train ,__df_validation\
          ,__idx_train ,__idx_validation

def df_bootstrap(df_data ,params = {}):
    default_params = {'bootstrap_params' : {'bootstrap_time' : 1
                                           ,'sample_ratio'   : 0.8
                                           ,'random_state'   : None
                                           }
                     ,'index_params' : {'index_save'      : 'N'
                                       ,'index_save_data' : 'N'
                                       ,'index_folder'    : '.\data_dpsd_expt'
                                       ,'index_filename'  : 'Boostrap'
                                       }
                     }
    params = update_append_nested(default_params ,params)

    from datetime import datetime
    import pytz
    __bootstraptime = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))

    dict_idx = {}
    for __time in range(params['bootstrap_params']['bootstrap_time']):
        _ ,_ ,__idx_train ,__idx_validation = df_sample(df_data
                                                       ,params['bootstrap_params']['sample_ratio']
                                                       ,params['bootstrap_params']['random_state'])
        dict_idx[__time] = {'idx_train'      : __idx_train
                           ,'idx_validation' : __idx_validation
                           }
    print(f"Bootstrap df: {params['bootstrap_params']['bootstrap_time']} times is done.")

    if params['index_params']['index_save'] == 'Y':
        import os
        import pickle
        if params['index_params']['index_save_data'] == 'Y':
            dict_idx = {'data' : df_data}
        index_filename = f"{params['index_params']['index_filename']}_{__bootstraptime.strftime('%Y%m%d_%H%M%S')}_{__bootstraptime.tzinfo.zone.replace('/' ,'_')}"
        with open(os.path.join(params['index_params']['index_folder'] ,index_filename + ".pkl"), 'wb') as f:
            pickle.dump(dict_idx ,f)
        print(f"Bootstrap df: indexes with data save in {index_filename}.pkl.")
        return dict_idx ,index_filename
    else:
        return dict_idx



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


