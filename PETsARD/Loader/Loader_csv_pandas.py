import pandas as pd


class Loader_csv_pandas:
    def __init__(self):
        pass

    def load(self, para_Loader):
        dict_setting = {}
        dict_setting['filepath_or_buffer'] = para_Loader['filepath']

        list_setting = ['sep', 'dtype', 'na_values']
        dict_setting.update({k: para_Loader[k] for k in list_setting})

        if para_Loader['header_exist']:
            dict_setting['header'] = 0
        else:
            dict_setting.update({
                'header': None,
                'names':  para_Loader['header_names']
            })

        return pd.read_csv(**dict_setting)
