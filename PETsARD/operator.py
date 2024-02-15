from typing import (
    Dict, List, Optional
)

import pandas as pd

from PETsARD.loader import Loader, Splitter


class Operator:
    """
    The interface of the objects used by Executor.run()
    """
    def __init__(self, config: dict):
        """
        Args:
            config (dict):
                A dictionary containing configuration parameters.
        """
        pass

    def run(self, input: dict):
        """
        Execute the module's functionality.

        Args:
            input (dict):
                A input dictionary contains module required input from Status.
                See Status.get_input_from_prev(module) for more details.
        """
        raise NotImplementedError

    def get_result(self):
        """
        Retrieve the result of the module's operation,
            as data storage varies between modules.

        Args
            tag (str):
                Specify (return) items of result.
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

        Attributes:
            loader (Loader):
                An instance of the Loader class initialized with the provided configuration.
        """
        super().__init__(config)
        self.loader = Loader(**config)

    def run(self, input: dict):
        """
        Executes the data loading process using the Loader instance.

        Args:
            input (dict): Loader input should contains nothing ({}).
        """
        self.loader.load()

    def get_result(self) -> pd.DataFrame:
        """
        Retrieve the loading result.
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

    def run(self, input: dict):
        """
        Executes the data splitting process using the Splitter instance.

        Args:
            input (dict): Splitter input should contains data (pd.DataFrame) and exclude_index (list).
        """
        self.splitter.split(**input)

    def get_result(self) -> pd.DataFrame:
        """
        Retrieve the splitting result.
            Due to Config force num_samples = 1, return 1st dataset is fine.
        """
        return self.splitter.data[1]