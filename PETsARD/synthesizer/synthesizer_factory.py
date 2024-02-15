from PETsARD.synthesizer.sdv import SDVFactory
from PETsARD.synthesizer.smartnoise import SmartNoiseFactory
from PETsARD.error import UnsupportedSynMethodError


class SynthesizerFactory:
    def __init__(self, data, **kwargs):
        method = kwargs.get('method', None)
        epsilon: float = kwargs.get('epsilon', 5.0)

        if method.startswith('sdv'):
            _Synthesizer = SDVFactory(
                data=data, method=method).create_synthesizer()
        elif method.startswith('smartnoise'):
            _Synthesizer = SmartNoiseFactory(data=data,
                                             method=method,
                                             epsilon=epsilon
                                             ).create_synthesizer()
        else:
            raise UnsupportedSynMethodError

        self.Synthesizer = _Synthesizer

    def create_synthesizer(self):
        return self.Synthesizer
