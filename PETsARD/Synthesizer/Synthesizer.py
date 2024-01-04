import pandas as pd

from .SynthesizerFactory import SynthesizerFactory


class Synthesizer:
    """
    Base class for all "Synthesizer".

    The "Synthesizer" class defines the common API
    that all the "Synthesizer" need to implement,
    as well as common functionality.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        synthesizing_method (str): The synthesizing method to be implemented.
        **kwargs: The other parameters.

    Return:
        None
    """

    def __init__(
        self,
        data: pd.DataFrame,
        synthesizing_method: str,
        **kwargs
    ) -> None:

        self.para: dict = {}
        self.para['Synthesizer']: dict = {
            'synthesizing_method': synthesizing_method.lower()
        }

        Synthesizer = SynthesizerFactory(
            data=data, **self.para['Synthesizer']
        ).create_synthesizer()

        self.data_ori: pd.DataFrame = data
        self.Synthesizer = Synthesizer

    def fit(self, **kwargs) -> None:
        """
        Fit the synthesizer.

        Args:
            **kwargs: The fitting parameters.

        Return:
            None
        """
        self.Synthesizer.fit(**kwargs)

    def sample(self, **kwargs) -> None:
        """
        Sample from the fitted synthesizer.

        Args:
            **kwargs: The sampling parameters.

        Return:
            None
        """
        self.data_syn = self.Synthesizer.sample(**kwargs)

    def fit_sample(self, **kwargs) -> None:
        """
        Fit and sample from the synthesizer.
        The combination of the methods `fit()` and `sample()`.

        Args:
            **kwargs: The fitting/sampling parameters.

        Return:
            None
        """
        self.data_syn: pd.DataFrame = self.Synthesizer.fit_sample(**kwargs)
