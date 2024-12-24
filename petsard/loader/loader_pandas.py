import pandas as pd

from petsard.loader.loader_base import LoaderBase


class LoaderPandasCsv(LoaderBase):
    """
    LoaderPandasCsv
        pandas.read_csv implementing of Loader
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration for the loader modules.

        Attr:
            config (dict): The configuration for the loader modules.
        """
        super().__init__(config)

    def load(self) -> pd.DataFrame:
        """
        Load and return the data

        Return:
            (pd.DataFrame)
                Data in csv by pd.DataFrame format.
        """
        pandas_config = {}

        # 1. set the filepath
        pandas_config['filepath_or_buffer'] = self.config['filepath']

        # 2. If header_names is not None, setting custom header names
        if self.config['header_names'] is not None:
            pandas_config.update({
                'header': None,
                'names':  self.config['header_names']
            })

        # 3. assign dtype and na_values
        list_setting = ['dtype', 'na_values']
        pandas_config.update({k: self.config[k] for k in list_setting})

        try:
            return pd.read_csv(**pandas_config)
        except Exception:
            raise FileNotFoundError


class LoaderPandasExcel(LoaderBase):
    """
    LoaderPandasExcel
        pandas.read_csv implementing of Loader
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration for the loader modules.

        Attr:
            config (dict): The configuration for the loader modules.
        """
        super().__init__(config)

    def load(self) -> pd.DataFrame:
        """
        Load and return the data

        Return:
            (pd.DataFrame)
                Data in excel by pd.DataFrame format.
        """
        pandas_config = {}

        # 1. set the filepath
        pandas_config['io'] = self.config['filepath']

        # 2. If header_names is not None, setting custom header names
        if self.config['header_names'] is not None:
            pandas_config.update({
                'header': None,
                'names':  self.config['header_names']
            })

        list_setting = ['dtype', 'na_values']
        pandas_config.update({k: self.config[k] for k in list_setting})

        try:
            return pd.read_excel(**pandas_config)
        except Exception:
            raise FileNotFoundError
