import pandas as pd

from PETsARD.synthesizer.sdv import SDVFactory
from PETsARD.synthesizer.smartnoise import SmartNoiseFactory
from PETsARD.error import UnsupportedSynMethodError


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

        # TODO: Map as Loader
        # TODO: verify method in __init__
        if self.config['method'].startswith('sdv'):
            self.Synthesizer = SDVFactory(**self.config).create()
        elif self.config['method'].startswith('smartnoise'):
            self.Synthesizer = SmartNoiseFactory(**self.config).create()
        else:
            raise UnsupportedSynMethodError

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
