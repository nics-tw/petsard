import pandas as pd

from PETsARD.synthesizer.synthesizer_factory import SynthesizerFactory


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
        method: str,
        epsilon: float = 5.0,
        **kwargs
    ) -> None:

        self.config: dict = {
            'method': method.lower(),
            'epsilon': epsilon
        }

        Synthesizer = SynthesizerFactory(
            data=data, **self.config
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
