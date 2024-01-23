import pandas as pd

from snsynth import Synthesizer


class SmartNoiseFactory:
    """
    Base class for all "SmartNoise".

    Manage the SmartNoise synthesizers.
    It allocates the task to the right SmartNoise synthesizer 
    based on the parameters.
    """
    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            **kwargs: The other parameters.

        Return:
            None
        """
        synthesizing_method: str = kwargs.get('synthesizing_method', None)
        eps: float = kwargs.get('epsilon', 5.0)

        if synthesizing_method.startswith('smartnoise'):
            self.Synthesizer = Synthesizer.\
                create(synthesizing_method.split('-')[1], epsilon=eps)
        else:
            raise ValueError(
                f"Synthesizer (SmartNoise - SmartNoiseFactory): "
                f"synthesizing_method {synthesizing_method} "
                f"didn't support."
            )

    def create_synthesizer(self):
        """
        Create synthesizer instance.
        Args:
            None
        Return:
            self.Synthesizer (synthesizer): The synthesizer instance.
        """
        return self.Synthesizer
