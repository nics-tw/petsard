import re

import pandas as pd

from petsard.error import ConfigError, UnsupportedMethodError
from petsard.loader import Loader, Metadata
from petsard.synthesizer.sdv import SDVFactory


class SynthesizerMap:
    """
    Mapping of Synthesizer.
    """

    DEFAULT: int = 0
    CUSTOM_DATA: int = 1
    SDV: int = 10

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value before 1st dash (-)

        Args:
            method (str): synthesizing method
        """
        try:
            # Get the string before 1st dash, if not exist, get emply ('').
            libname_match = re.match(r"^[^-]*", method)
            libname = libname_match.group() if libname_match else ""
            return cls.__dict__[libname.upper()]
        except KeyError:
            raise UnsupportedMethodError


class Synthesizer:
    """
    The Synthesizer class is responsible for creating and fitting a synthesizer model,
    as well as generating synthetic data based on the fitted model.
    """

    def __init__(self, method: str, **kwargs) -> None:
        """
        Args:
            method (str): The method to be used for synthesizing the data.

        Attributes:
            config (dict):
                A dictionary containing the configuration parameters for the synthesizer.
        """
        self.config: dict = kwargs
        self.config["method"] = method.lower()
        self.config["method_code"] = SynthesizerMap.map(self.config["method"])

        # result in self.data_syn
        self.data_syn: pd.DataFrame = None

    def create(self, data: pd.DataFrame, metadata: Metadata = None) -> None:
        """
        Create a synthesizer object with the given data.

        Args:
            data (pd.DataFrame): The input data for synthesizing.
            metadata (Metadata, default=None): The metadata class of the data.
        """
        self.config["data"] = data
        self.config["metadata"] = metadata

        if self.config["method_code"] == SynthesizerMap.DEFAULT:
            # default will use SDV - GaussianCopula
            self.config["method"] = "sdv-single_table-gaussiancopula"
            self.synthesizer = SDVFactory(**self.config).create()
        elif self.config["method_code"] == SynthesizerMap.CUSTOM_DATA:
            if "filepath" not in self.config:
                raise ConfigError
            self.loader = Loader(
                **{
                    k: self.config.get(k)
                    for k in [
                        "filepath",
                        "column_types",
                        "header_names",
                        "na_values",
                    ]
                    if self.config.get(k) is not None
                }
            )
        elif self.config["method_code"] == SynthesizerMap.SDV:
            self.synthesizer = SDVFactory(**self.config).create()
        else:
            raise UnsupportedMethodError

    def fit(self) -> None:
        """
        Fits the synthesizer model with the given parameters.
        """
        if self.config["method_code"] == SynthesizerMap.CUSTOM_DATA:
            self.loader.load()
        else:
            self.synthesizer.fit()

    def sample(self, **kwargs) -> None:
        """
        This method generates a sample using the Synthesizer object.

        Return:
            None. The synthesized data is stored in the `data_syn` attribute.
        """
        if self.config["method_code"] == SynthesizerMap.CUSTOM_DATA:
            self.data_syn = self.loader.data
        else:
            self.data_syn = self.synthesizer.sample(**kwargs)

    def fit_sample(self, **kwargs) -> None:
        """
        Fit and sample from the synthesizer.
        The combination of the methods `fit()` and `sample()`.

        Return:
            None. The synthesized data is stored in the `data_syn` attribute.
        """
        if self.config["method_code"] == SynthesizerMap.CUSTOM_DATA:
            self.fit()
            self.data_syn = self.loader.data
        else:
            self.data_syn = self.synthesizer.fit_sample(**kwargs)
