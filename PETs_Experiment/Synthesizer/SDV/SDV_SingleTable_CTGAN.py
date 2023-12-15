from .SDV_SingleTable import SDV_SingleTable

class SDV_SingleTable_CTGAN(SDV_SingleTable):
    def __init__(self,   data, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method = 'CTGAN'

        # metadata already create in SDV_SingleTable
        from sdv.single_table import CTGANSynthesizer
        self._Synthesizer = CTGANSynthesizer(self.metadata)