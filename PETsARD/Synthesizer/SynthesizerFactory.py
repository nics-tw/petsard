from .SDV.SDVFactory import SDVFactory
import pandas as pd


class SynthesizerFactory:
    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        synthesizing_method = kwargs.get('synthesizing_method', None)

        if synthesizing_method.startswith('sdv'):
            _Synthesizer = SDVFactory(data=data,
                                      synthesizing_method=synthesizing_method).create_synthesizer()
        else:
            raise ValueError(
                f"Synthesizer - SynthesizerFactory: synthesizing_method {synthesizing_method} didn't support.")

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
