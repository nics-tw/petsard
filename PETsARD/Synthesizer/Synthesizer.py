import pandas as pd

from PETsARD.Synthesizer.SynthesizerFactory import SynthesizerFactory


class Synthesizer:
    """
    Base class for all "Synthesizer".

    The "Synthesizer" class defines the common API
    that all the "Synthesizer" need to implement,
    as well as common functionality.

    ...
    Methods:
        Synthesizer(DataFrame): Synthesizing specified DataFrame.
        Returns:
            DataFrame: A pandas DataFrame that input data after synthesizing
    ...

    Args:

    """

    def __init__(
        self,
        data: pd.DataFrame,
        synthesizing_method: str,
        epsilon: float = 5.0,
        **kwargs
    ) -> None:

        self.para: dict = {}
        self.para['Synthesizer']: dict = {
            'synthesizing_method': synthesizing_method.lower(),
            'epsilon': epsilon
        }

        Synthesizer = SynthesizerFactory(
            data=data, **self.para['Synthesizer']
        ).create_synthesizer()

        self.data_ori = data
        self.Synthesizer = Synthesizer

    def fit(self, **kwargs):
        self.Synthesizer.fit(**kwargs)

    def sample(self, **kwargs):
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
