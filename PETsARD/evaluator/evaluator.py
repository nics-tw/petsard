import importlib.util
import re

import pandas as pd

from PETsARD.evaluator.anonymeter import Anonymeter
from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.evaluator.mlutlity import MLUtility
from PETsARD.evaluator.sdmetrics import SDMetrics
from PETsARD.evaluator.automl import AutoML
from PETsARD.error import ConfigError, UnsupportedMethodError


class EvaluatorMap():
    """
    Mapping of Evaluator.
    """
    DEFAULT:       int = 0
    CUSTOM_METHOD: int = 1
    ANONYMETER:    int = 10
    SDMETRICS:     int = 11
    AUTOML:        int = 12
    MLUTILITY:     int = 13

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
    """
    def __init__(self, method: str, custom_method: dict=None, **kwargs):
        """
        Args:
            method (str):
                The method of how you evaluating data. Case insensitive.
                    The format should be: {library name}_{function name},
                    e.g., 'anonymeter_singlingout_univariate'.
            custom_method (dict):
                The dictionary contains the custom method information.
                It should include:
                    - filepath (str): The path to the custom method file.
                    - method (str): The method name in the custom method file.

        Attr:
            config (dict):
                The dictionary contains the configuration information.
                It should include:
                    - method (str): The method of how you evaluating data.
                    - method_code (int): The method code of how you evaluating data.
            evaluator (EvaluatorBase):
                The evaluator object.
            result (dict):
                The dictionary contains the evaluation result.
        """
        self.config = kwargs
        self.config['method'] = method.lower()
        self.evaluator: EvaluatorBase = None
        self.result = None

        method_code: int = EvaluatorMap.map(self.config['method'])
        self.config['method_code'] = method_code
        if method_code == EvaluatorMap.DEFAULT:
            # default will use SDMetrics - QualityReport
            self.config['method'] = 'sdmetrics-single_table-qualityreport'
            self.evaluator = SDMetrics(config=self.config)
        elif method_code == EvaluatorMap.CUSTOM_METHOD:
            # custom method
            self.config['custom_method'] = custom_method
            if 'filepath' not in self.config['custom_method']\
                or 'method' not in self.config['custom_method']:
                raise ConfigError

            try:
                spec = importlib.util.spec_from_file_location(
                    "module.name", self.config['custom_method']['filepath'])
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                evaluator = getattr(
                    module,
                    self.config['custom_method']['method']
                )
            except:
                raise ConfigError
            self.evaluator = evaluator(config=self.config)
        elif method_code == EvaluatorMap.ANONYMETER:
            self.evaluator = Anonymeter(config=self.config)
        elif method_code == EvaluatorMap.SDMETRICS:
            self.evaluator = SDMetrics(config=self.config)
        elif method_code == EvaluatorMap.AUTOML:
            self.evaluator = AutoML(config=self.config)
        elif method_code == EvaluatorMap.MLUTILITY:
            self.evaluator = MLUtility(config=self.config)
        else:
            raise UnsupportedMethodError

    def create(self, data: dict) -> None:
        """
        Create a Evaluator object with the given data.

        Args:
            data (dict)
                The dictionary contains necessary information.
                For Anonymeter and MLUtility requirements:
                    data = {
                        'ori' : pd.DataFrame   # Original data used for synthesis
                        'syn' : pd.DataFrame   # Synthetic data generated from 'ori'
                        'control: pd.DataFrame # Original data but NOT used for synthesis
                    }
                    Note: So it is recommended to split your original data before synthesizing it.
                    (We recommend to use our Splitter!)
                For SDMetrics and AutoML requirements:
                    data = {
                        'ori' : pd.DataFrame   # Original data used for synthesis
                        'syn' : pd.DataFrame   # Synthetic data generated from 'ori'
                    }
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
            pd.DataFrame: A dataFrame with the global evaluation result.
                One row only for representing the whole data result.
        """
        return self.evaluator.get_global()

    def get_columnwise(self) -> pd.DataFrame:
        """
        Returns the column-wise evaluation result.

        Returns:
            pd.DataFrame: A dataFrame with the column-wise evaluation result.
                Each row contains one column in original data.
        """
        return self.evaluator.get_columnwise()

    def get_pairwise(self) -> pd.DataFrame:
        """
        Retrieves the pairwise evaluation result.

        Returns:
            pd.DataFrame: A dataFrame with the pairwise evaluation result.
                Each row contains column x column in original data.
        """
        return self.evaluator.get_pairwise()
