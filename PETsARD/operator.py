from typing import (
    Dict, List, Optional
)

import pandas as pd

from PETsARD.loader import Loader, Splitter
from PETsARD.error import ConfigError


class Operator:
    """
    Operator
        The parent class for every module's decorator: {module_name}Operato,
        unifying the method name as .run(), .get_result().
    """
    def __init__(self, config: dict):
        pass

    def run(self):
        """
        Execute the module's functionality.
        """
        raise NotImplementedError

    def get_result(self, tag: str = None):
        """
        Retrieve the result of the module's operation, as data storage varies between modules.
        """
        raise NotImplementedError


class LoaderOperator(Operator):
    """
    LoaderOperator is responsible for loading data using the configured Loader instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict):
                A dictionary containing configuration parameters for the Loader.
        ...
        Attributes:
            loader (Loader):
                An instance of the Loader class initialized with the provided configuration.
        """
        super().__init__(config)
        self.loader = Loader(**config)

    def run(self):
        """
        Executes the data loading process using the Loader instance.
        """
        self.loader.load()

    def get_result(self, tag: str=None) -> pd.DataFrame:
        """
        Retrieve the loading result.
        ...
        Args
            tag (str)
                Inherited from Operator. Not applicable.
        """
        return self.loader.data
    

class SplitterOperator(Operator):
    """
    SplitterOperator is responsible for splitting data
        using the configured Loader instance as a decorator.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.splitter = Splitter(**config)

    def run(self, data: pd.DataFrame, exclude_index: Optional[Dict[int, List[int]]] = None):
        """
        Executes the data splitting process using the Splitter instance.
        """
        self.splitter.split(data, exclude_index)

    def get_result(self, tag: str) -> pd.DataFrame:
        """
        Retrieve the splitting result.
        Due to Config force num_samples = 1, return 1st dataset is fine.
        ...
        Args
            tag (str)
                Get whether train or validation data.
        """
        if tag in ['train','validation']:
            return self.splitter.data[1][tag]
        else:
            raise ConfigError