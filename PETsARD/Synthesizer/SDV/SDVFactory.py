class SDVFactory:
    def __init__(self, data, **kwargs):
        synthesizing_method = kwargs.get('synthesizing_method', None)

        if synthesizing_method.startswith('sdv-singletable'):
            from .SDV_SingleTableFactory import SDV_SingleTableFactory
            _Synthesizer = SDV_SingleTableFactory(data=data, synthesizing_method=synthesizing_method
                                                  ).create_synthesizer()
        else:
            raise ValueError(
                f"Synthesizer (SDV - SDVFactory): synthesizing_method {synthesizing_method} didn't support.")

        self.Synthesizer = _Synthesizer

    def create_synthesizer(self):
        return self.Synthesizer






        # _para_SDV = kwargs.get('SDV', None)
        # if _para_SDV is not None:
        #     _para_SingleTable = {k.replace('SingleTable_', '', 1): v for k, v in _para_SDV.items(
        #     ) if k.startswith("SingleTable_")}
        # else:
        #     _para_SingleTable = {}
        # , **_para_SingleTable