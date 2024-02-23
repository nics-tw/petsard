import pandas as pd


class EvaluatorBase():
    """
    Base class for Describers/Evaluators.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.

        Attributes:
            config (dict):
                A dictionary containing the configuration settings.
            data (dict):
                A dictionary to store evaluation data. Default is an empty.
            result (dict):
                A dictionary to store the result of the description/evaluation. Default is an empty.
        """
        self.config: dict = config
        self.data: dict = {}
        self.result: dict = {}

    def create(self, data: dict):
        """
        Create the Describer/Evaluator. This method should be implemented by subclasses.

        Args:
            data (dict): The data required for description/evaluation.
        """
        raise NotImplementedError

    def eval(self):
        """
        Describes/Evaluates the data. This method should be implemented by subclasses.
        """
        raise NotImplementedError

    def get_global(self) -> pd.DataFrame:
        """
        Get the global result of the description/evaluation.
            Only one row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError

    def get_columnwise(self) -> pd.DataFrame:
        """
        Get the column-wise result of the description/evaluation.
            Each column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError

    def get_pairwise(self) -> pd.DataFrame:
        """
        Get the pair-wise result of the description/evaluation.
            Each column x column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        raise NotImplementedError
