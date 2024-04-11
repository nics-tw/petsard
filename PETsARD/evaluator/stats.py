from abc import ABC, abstractmethod

import pandas as pd
from pandas.api.types import is_numeric_dtype

from PETsARD.util import safe_round


class StatsBase(ABC):
    """
    Base class for statistics evaluation.
    """

    def __init__(self):
        """
        Attr:
            data (dict[str, pd.Series]): The data to be evaluated.
        """
        self.data: dict[str, pd.Series] = None

    def create(self, data: dict[str, pd.Series]):
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Raises:
            TypeError: If the data type verification fails.
        """
        self.data = data
        self._create()
        self.verify: dict = {}
        if self._verify_dtype():
            self.verify['dtype'] = True
        else:
            raise TypeError

    @abstractmethod
    def _create(self):
        """
        Performs the actual creation of statistics.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def _verify_dtype(self) -> bool:
        """
        Verifies the data type of the statistics.

        Returns:
            (bool): True if the data type verification passes, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def eval(self) -> int | float:
        """
        Evaluates the statistics and returns the result.
            safe_round is used to round 6 digits the result if it is a float.

        Returns:
            (int | float): The result of the statistics evaluation.
        """
        result: int | float = self._eval()
        if isinstance(result, float):
            result = safe_round(result)
        return result

    @abstractmethod
    def _eval(self) -> int | float:
        """
        Performs the evaluation of the statistics.

        Returns:
            (int | float): The result of the statistics evaluation.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError


class StatsColumnwise(StatsBase):
    """
    A class for calculating column-wise statistics.
        Inherits from StatsBase.
    """

    def __init__(self):
        super().__init__()

    def _create(self):
        """
        Attributes:
            col (pd.Series): The column data.
        """
        self.col: pd.Series = self.data['col']


class StatsMean(StatsColumnwise):
    """
    A class of column-wise statistic for the mean.
        Inherits from StatsColumnwise.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the column's data type is numeric, False otherwise.
        """
        return is_numeric_dtype(self.col)

    def _eval(self) -> float:
        """
        Returns:
            (float): The mean value of the column.
        """
        return self.col.mean()


class StatsStd(StatsColumnwise):
    """
    A class of column-wise statistic for the standard deviation.
        Inherits from StatsColumnwise.
    """

    def _verify_dtype(self,) -> bool:
        """
        Returns:
            (bool): True if the column's data type is numeric, False otherwise.
        """
        return is_numeric_dtype(self.col)

    def _eval(self) -> float:
        """
        Returns:
            (float): The standard deviation of the column.
        """
        return self.col.std()


class StatsNUnique(StatsColumnwise):
    """
    A class of column-wise statistic for the number of unique values.
        Inherits from the StatsColumnwise.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the data type is 'category', False otherwise.
        """
        return self.col.dtype == 'category'

    def _eval(self) -> int:
        """
        Returns:
            (int): The number of unique values in the column.
        """
        return self.col.nunique(dropna=True)
