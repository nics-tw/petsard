class SynthesizerFactory:
    def __init__(self, data, **kwargs):
        synthesizing_method = kwargs.get('synthesizing_method', None)

        if synthesizing_method.startswith('sdv'):
            from .SDV.SDVFactory import SDVFactory
            _Synthesizer = SDVFactory(data=data, synthesizing_method=synthesizing_method
                                      ).create_synthesizer()
        else:
            raise ValueError(
                f"Synthesizer - SynthesizerFactory: synthesizing_method {synthesizing_method} didn't support.")

        self.Synthesizer = _Synthesizer

    def create_synthesizer(self):
        return self.Synthesizer