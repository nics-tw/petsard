import pandas as pd

from PETsARD.synthesizer.sdv.sdv_factory import SDVFactory


class SynthesizerFactory:
    def __init__(self, data, **kwargs):
        synthesizing_method = kwargs.get('synthesizing_method', None)

        if synthesizing_method.startswith('sdv'):
            _Synthesizer = SDVFactory(data=data, synthesizing_method=synthesizing_method
                                      ).create_synthesizer()
        else:
            raise ValueError(
                f"Synthesizer - SynthesizerFactory: "
                f"synthesizing_method {synthesizing_method} "
                f"didn't support."
            )

        self.Synthesizer = _Synthesizer

    def create_synthesizer(self):
        return self.Synthesizer
