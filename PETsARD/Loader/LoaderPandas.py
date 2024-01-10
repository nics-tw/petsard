import pandas as pd

from .LoaderBase import LoaderBase


class LoaderPandasCsv(LoaderBase):
    """
    LoaderPandasCsv
        pandas.read_csv implementing of Loader
    """

    def __init__(self, para_Loader: dict):
        super().__init__(para_Loader)

    def load(self) -> pd.DataFrame:
        """
        Load and return the data
        ...
        Return:
            (pd.DataFrame)
                Data in csv by pd.DataFrame format.
        """
        dict_setting = {}
        dict_setting['filepath_or_buffer'] = self.para_Loader['filepath']

        list_setting = ['sep', 'dtype', 'na_values']
        dict_setting.update({k: self.para_Loader[k] for k in list_setting})

        if self.para_Loader['header_exist']:
            dict_setting['header'] = 0
        else:
            dict_setting.update({
                'header': None,
                'names':  self.para_Loader['header_names']
            })

        return pd.read_csv(**dict_setting)


class LoaderPandasExcel(LoaderBase):
    """
    LoaderPandasExcel
        pandas.read_csv implementing of Loader
    """

    def __init__(self, para_Loader: dict):
        super().__init__(para_Loader)

    def load(self) -> pd.DataFrame:
        """
        Load and return the data
        ...
        Return:
            (pd.DataFrame)
                Data in excel by pd.DataFrame format.
        """
        dict_setting = {}
        dict_setting['io'] = self.para_Loader['filepath']

        list_setting = ['sheet_name', 'dtype', 'na_values']
        dict_setting.update({k: self.para_Loader[k] for k in list_setting})

        if self.para_Loader['header_exist']:
            dict_setting['header'] = 0
        else:
            dict_setting.update({
                'header': None,
                'names':  self.para_Loader['header_names']
            })

        try:
            return pd.read_excel(**dict_setting)
        except ValueError as ex:
            if "Worksheet named" in str(ex) and "not found" in str(ex):
                print(
                    f"Loader (PandasExcel): "
                    f"Sheet name {dict_setting['sheet_name']} "
                    f"does NOT exist."
                )
            else:
                print(
                    f"Loader (PandasExcel): "
                    f"An unknown ValueError occurred: \n"
                    f"{ex}"
                )
