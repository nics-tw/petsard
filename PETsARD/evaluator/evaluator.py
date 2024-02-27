import re

import pandas as pd

from PETsARD.evaluator.anonymeter import Anonymeter
from PETsARD.evaluator.sdmetrics import SDMetrics
from PETsARD.error import ConfigError, UnsupportedMethodError


class EvaluatorMap():
    """
    Mapping of Evaluator.
    """
    DEFAULT:       int = 0
    CUSTOM_METHOD: int = 1
    ANONYMETER:    int = 10
    SDMETRICS:     int = 11

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value before 1st dash (-)

        Args:
            method (str): evaluating method
        """
        try:
            # Get the string before 1st dash, if not exist, get emply ('').
            libname_match = re.match(r'^[^-]*', method)
            libname = libname_match.group() if libname_match else ''
            return cls.__dict__[libname.upper()]
        except KeyError:
            raise UnsupportedMethodError


class Evaluator:
    """
    Base class for all "Evaluator".

    The "Evaluator" class defines the common API
    that all "Evaluators" need to implement, as well as common functionality.

    Args:
        method (str):
            The method of how you evaluating data. Case insensitive.
                The format should be: {library name}{function name},
                e.g., 'anonymeter_singlingout_univariate'.
    """
    def __init__(self, method: str, **kwargs):
        self.config = kwargs
        self.config['method'] = method.lower()
        self.evaluator = None

        method_code: int = EvaluatorMap.map(self.config['method'])
        self.config['method_code']: int = method_code
        if method_code == EvaluatorMap.DEFAULT:
            # default will use SDMetrics - QualityReport
            self.config['method'] = 'sdmetrics-single_table-qualityreport'
            self.evaluator = SDMetrics(config=self.config)
        elif method_code == EvaluatorMap.ANONYMETER:
            self.evaluator = Anonymeter(config=self.config)
        elif method_code == EvaluatorMap.SDMETRICS:
            self.evaluator = SDMetrics(config=self.config)
        else:
            raise UnsupportedMethodError

    def create(self, data: dict) -> None:
        """
        Create a Evaluator object with the given data.

        Args:
            data (dict)
                The dictionary contains necessary information.
                For now, we adhere to the Anonymeter requirements,
                so you should include:
                data = {
                    'ori' : pd.DataFrame   # Original data used for synthesis
                    'syn' : pd.DataFrame   # Synthetic data generated from 'ori'
                    'control: pd.DataFrame # Original data but NOT used for synthesis
                }
                Note: So it is recommended to split your original data before synthesizing it.
                    (We recommend to use our pipeline!)
        """
        self.evaluator.create(data=data)

    def eval(self) -> None:
        """
        eval()
            Call the evaluating method within implementation after Factory.
        """
        self.evaluator.eval()
        self.result = self.evaluator.result

    def get_global(self) -> pd.DataFrame:
        """
        Returns the global evaluation result.

        Returns:
            pd.DataFrame: A DataFrame with the global evaluation result.
                One row only for representing the whole data result.
        """
        return self.evaluator.get_global()

    def get_columnwise(self) -> pd.DataFrame:
        """
        Returns the column-wise evaluation result.

        Returns:
            pd.DataFrame: A DataFrame with the column-wise evaluation result.
                Each row contains one column in original data.
        """
        return self.evaluator.get_columnwise()

    def get_pairwise(self) -> pd.DataFrame:
        """
        Retrieves the pairwise evaluation result.

        Returns:
            pd.DataFrame: A DataFrame with the pairwise evaluation result.
                Each row contains column x column in original data.
        """
        return self.evaluator.get_pairwise()
