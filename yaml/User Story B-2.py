import itertools
from typing import Union

import pandas as pd

from PETsARD.evaluator.evaluator_base import EvaluatorBase


class UserStory_B2(EvaluatorBase):
    """
    This class demo User Story B-2: custom_method
    """

    def __init__(self, config: dict):
        """
        Initializes the UserStory_5 object.

        Args:
            config (dict): The configuration dictionary.

        Attributes:
            config (dict): The configuration dictionary.
            columns (list): The columns of the data.
            result (dict): The evaluation result.
        """
        super().__init__(config=config)

    def create(self, data: dict) -> None:
        """
        Creates the object.

        Args:
            data (dict): The data required for description/evaluation.
        """
        self.columns = data['ori'].columns

    def eval(self) -> None:
        """
        Evaluates the object.
        """
        self.result = {'score': 100}

    def get_global(self) -> Union[pd.DataFrame, None]:
        """
        Returns the global evaluation result.
        """
        return pd.DataFrame(self.result, index=['result'])

    def get_columnwise(self) -> Union[pd.DataFrame, None]:
        """
        Returns the column-wise evaluation result.
        """
        return pd.DataFrame(self.result, index=self.columns)

    def get_pairwise(self) -> Union[pd.DataFrame, None]:
        """
        Returns the pairwise evaluation result.
        """
        index = [
            (col1, col2)
            for i, col1 in enumerate(self.columns)
            for j, col2 in enumerate(self.columns)
            if j <= i
        ]
        return pd.DataFrame(
            self.result,
            index=pd.MultiIndex.from_tuples(index)
        )
