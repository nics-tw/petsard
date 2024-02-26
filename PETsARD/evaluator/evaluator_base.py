from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd

from PETsARD.error import ConfigError


class EvaluatorBase(ABC):
    """
    Base class for Describers/Evaluators.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.
                - method (str): The method of how you evaluating data.
                - other parameters should be defined in the module class (Describer/Evaluator)

        Attributes:
            config (dict):
                A dictionary containing the configuration settings.
            data (Dict[str, pd.DataFrame]):
                A dictionary to store evaluation data. Default is an empty.
            result (dict):
                A dictionary to store the result of the description/evaluation. Default is an empty.
        """
        if 'method' not in config:
            raise ConfigError

        self.config: dict = config
        self.data: Dict[str, pd.DataFrame] = {}
        self.result: dict = {}

    @abstractmethod
    def create(self, data: dict) -> None:
        """
        Create the Describer/Evaluator. This method should be implemented by subclasses.

        Args:
            data (dict): The data required for description/evaluation.
        """
        raise NotImplementedError

    @abstractmethod
    def eval(self) -> None:
        """
        Describes/Evaluates the data. This method should be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def get_global(self) -> pd.DataFrame:
        """
        Get the global result of the description/evaluation.
            Only one row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError

    @abstractmethod
    def get_columnwise(self) -> pd.DataFrame:
        """
        Get the column-wise result of the description/evaluation.
            Each column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError

    @abstractmethod
    def get_pairwise(self) -> pd.DataFrame:
        """
        Get the pair-wise result of the description/evaluation.
            Each column x column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError
