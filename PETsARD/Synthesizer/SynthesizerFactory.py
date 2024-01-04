import pandas as pd

from .SDV.SDVFactory import SDVFactory


class SynthesizerFactory:
    """
    Manage the synthesizers.
    It allocates the task to the right synthesizer factory
    based on the parameters.

    Args:
        data (pd.DataFrame): The data to be synthesized from.
        **kwargs: The other parameters.

    Return:
        None

    TODO As AnonymeterMethodMap, use class define mapping of string and int,
         don't use string condition.
    """

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        synthesizing_method: str = kwargs.get('synthesizing_method', None)

        if synthesizing_method.startswith('sdv'):
            _Synthesizer = SDVFactory(
                data=data,
                synthesizing_method=synthesizing_method
            ).create_synthesizer()
        else:
            raise ValueError(
                f"Synthesizer - SynthesizerFactory: "
                f"synthesizing_method {synthesizing_method} "
                f"didn't support."
            )

        self.Synthesizer = _Synthesizer

    def create_synthesizer(self):
        """
        Create synthesizer instance.

        Args:
            None

        Return:
            self.Synthesizer (synthesizer): The synthesizer instance.
        """
        return self.Synthesizer
