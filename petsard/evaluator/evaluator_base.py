from abc import ABC, abstractmethod
from typing import Union

import pandas as pd

from petsard import Metadata
from petsard.error import ConfigError
from petsard.util import safe_astype


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
            data (dict[str, pd.DataFrame]):
                A dictionary to store evaluation data. Default is an empty.
            result (dict):
                A dictionary to store the result of the description/evaluation. Default is an empty.
        """
        if "method" not in config:
            raise ConfigError

        self.config: dict = config
        self.data: dict[str, pd.DataFrame] = {}
        self.result: dict = {}

    def create(self, data: dict) -> None:
        """
        Create the Describer/Evaluator.

        Args:
            data (dict): The data required for description/evaluation.
        """
        if not all(key == "data" for key in data):
            if "ori" not in data:
                raise ConfigError

            metadata: Metadata = Metadata()
            metadata.build_metadata(data=data["ori"])
            other_keys: list[str] = [key for key in data.keys() if key != "ori"]
            for other_key in other_keys:
                data[other_key] = self._align_dtypes(
                    data[other_key],
                    metadata,
                )
        self._create(data)

    def _align_dtypes(
        self,
        data: pd.DataFrame,
        metadata: Metadata,
    ) -> pd.DataFrame:
        """
        Align the data types between the metadata from ori data
            and the data to be aligned.

        Args:
            data (pd.DataFrame): The data to be aligned.
            metadata (Metadata): The metadata of ori data.

        Return:
            (pd.DataFrame): The aligned data.
        """
        for col, val in metadata.metadata["col"].items():
            data[col] = safe_astype(data[col], val["dtype"])

        return data

    @abstractmethod
    def _create(self, data: dict) -> None:
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

    def get_global(self) -> Union[pd.DataFrame, None]:
        """
        Get the global result of the description/evaluation.
            Only one row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError

    def get_columnwise(self) -> Union[pd.DataFrame, None]:
        """
        Get the column-wise result of the description/evaluation.
            Each column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError

    def get_pairwise(self) -> Union[pd.DataFrame, None]:
        """
        Get the pair-wise result of the description/evaluation.
            Each column x column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError
