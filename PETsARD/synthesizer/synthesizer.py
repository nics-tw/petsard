import re

import pandas as pd

from PETsARD.synthesizer.sdv import SDVFactory
from PETsARD.synthesizer.smartnoise import SmartNoiseFactory
from PETsARD.error import UnsupportedMethodError


class SynthesizerMap():
    """
    Mapping of Synthesizer.
    """
    SDV:        int = 1
    SMARTNOISE: int = 2

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value before 1st dash (-)

        Args:
            method (str): synthesizing method
        """
        try:
            # Get the string before 1st dash, if not exist, get emply ('').
            libname_match = re.match(r'^[^-]*', method)
            libname = libname_match.group() if libname_match else ''
            return cls.__dict__[libname.upper()]
        except KeyError:
            raise UnsupportedMethodError


class Synthesizer:
    """
    The Synthesizer class is responsible for creating and fitting a synthesizer model,
    as well as generating synthetic data based on the fitted model.
    """

    def __init__(self, method: str, epsilon: float = 5.0, **kwargs) -> None:
        """
        Attributes:
            config (dict):
                A dictionary containing the configuration parameters for the synthesizer.

        Args:
            method (str): The method to be used for synthesizing the data.
            epsilon (float): The privacy parameter for the synthesizer. Default: 5.0.
        """
        self.config: dict = {
            'method': method.lower(),
            'epsilon': epsilon
        }

    def create(self, data: pd.DataFrame) -> None:
        """
        Create a synthesizer object with the given data.

        Args:
            data (pd.DataFrame): The input data for synthesizing.
        """
        self.config['data'] = data

        # TODO: verify method in __init__
        method_code = SynthesizerMap.map(self.config['method'])
        if method_code == SynthesizerMap.SDV:
            self.Synthesizer = SDVFactory(**self.config).create()
        elif method_code == SynthesizerMap.SMARTNOISE:
            self.Synthesizer = SmartNoiseFactory(**self.config).create()
        else:
            raise UnsupportedMethodError

    def fit(self, **kwargs) -> None:
        """
        Fits the synthesizer model with the given parameters.
        """
        self.Synthesizer.fit(**kwargs)

    def sample(self, **kwargs) -> None:
        """
        This method generates a sample using the Synthesizer object.

        Return:
            None. The synthesized data is stored in the `data_syn` attribute.
        """
        self.data_syn = self.Synthesizer.sample(**kwargs)

    def fit_sample(self, **kwargs) -> None:
        """
        Fit and sample from the synthesizer.
        The combination of the methods `fit()` and `sample()`.

        Return:
            None. The synthesized data is stored in the `data_syn` attribute.
        """
        self.data_syn: pd.DataFrame = self.Synthesizer.fit_sample(**kwargs)
