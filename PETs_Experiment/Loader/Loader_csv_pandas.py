class Loader_csv_pandas:
    def __init__(self):
        pass

    def load(self ,para_Loader):
        __dict_setting = {}
        __dict_setting['filepath_or_buffer'] = para_Loader['filepath']

        __list_setting = ['sep' ,'dtype' ,'na_values']
        __dict_setting.update({k: para_Loader[k] for k in __list_setting})

        if para_Loader['header_exist']:
            __dict_setting['header'] = 0
        else:
            __dict_setting.update({'header' : None
                                  ,'names'  : para_Loader['header_names']
                                  })

        import pandas as pd
        return pd.read_csv(**__dict_setting)
