import pandas as pd

from .Loader import Loader


class Loader_csv_pandas(Loader):
    def __init__(self):
        super().__init__()

    def load(self, para_Loader: dict) -> pd.DataFrame:
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


class Loader_excel_pandas(Loader):
    def __init__(self):
        super().__init__()

    def load(self, para_Loader: dict) -> pd.DataFrame:
        dict_setting = {}
        dict_setting['io'] = para_Loader['filepath']

        list_setting = ['sheet_name', 'dtype', 'na_values']
        dict_setting.update({k: para_Loader[k] for k in list_setting})

        if para_Loader['header_exist']:
            dict_setting['header'] = 0
        else:
            dict_setting.update({
                'header': None,
                'names':  para_Loader['header_names']
            })

        try:
            return pd.read_excel(**dict_setting)
        except ValueError as ex:
            if "Worksheet named" in str(ex) and "not found" in str(ex):
                print(
                    f"Loader (Excel_pandas): "
                    f"Sheet name {dict_setting['sheet_name']} "
                    f"does NOT exist."
                )
            else:
                print(
                    f"Loader (Excel_pandas): "
                    f"An unknown ValueError occurred: \n"
                    f"{ex}"
                )
