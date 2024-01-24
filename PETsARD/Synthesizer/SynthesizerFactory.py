import pandas as pd

from PETsARD.Synthesizer.SDV.SDVFactory import SDVFactory
from PETsARD.Synthesizer.smartnoise import SmartNoiseFactory


class SynthesizerFactory:
    def __init__(self, data, **kwargs):
        synthesizing_method = kwargs.get('synthesizing_method', None)
        epsilon: float = kwargs.get('epsilon', 5.0)

        if synthesizing_method.startswith('sdv'):
            _Synthesizer = SDVFactory(data=data, 
                                      synthesizing_method=synthesizing_method
                                      ).create_synthesizer()
        elif synthesizing_method.startswith('smartnoise'):
            _Synthesizer = SmartNoiseFactory(data=data,
                                synthesizing_method=synthesizing_method,
                                epsilon=epsilon
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
