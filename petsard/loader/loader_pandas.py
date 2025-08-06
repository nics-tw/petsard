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
        # 1. set the filepath as first positional argument
        filepath = self.config["filepath"]

        pandas_config = {}

        # 2. If header_names is not None, setting custom header names
        if self.config.get("header_names") is not None:
            pandas_config.update({"header": 0, "names": self.config["header_names"]})
        else:
            # Default header settings to match original behavior
            pandas_config.update({"header": "infer", "names": None})

        # 3. assign dtype and na_values
        list_setting = ["dtype", "na_values"]
        pandas_config.update(
            {k: self.config[k] for k in list_setting if k in self.config}
        )

        try:
            return pd.read_csv(filepath, **pandas_config)
        except Exception as e:
            raise FileNotFoundError from e


class LoaderPandasExcel(LoaderBase):
    """
    LoaderPandasExcel
        pandas.read_excel implementing of Loader
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
        # 檢查 openpyxl 是否已安裝
        try:
            import openpyxl
        except ImportError:
            from petsard.exceptions import ConfigError

            raise ConfigError(
                "openpyxl is required to read Excel files. "
                "Please install it with: pip install petsard[xlsx]"
            )

        # 1. set the filepath as first positional argument
        filepath = self.config["filepath"]

        pandas_config = {}

        # 2. If header_names is not None, setting custom header names
        if self.config.get("header_names") is not None:
            pandas_config.update({"header": 0, "names": self.config["header_names"]})
        else:
            # Default header settings to match original behavior
            pandas_config.update({"header": "infer", "names": None})

        # 3. assign dtype and na_values
        list_setting = ["dtype", "na_values"]
        pandas_config.update(
            {k: self.config[k] for k in list_setting if k in self.config}
        )

        try:
            return pd.read_excel(filepath, **pandas_config)
        except Exception as e:
            raise FileNotFoundError from e
