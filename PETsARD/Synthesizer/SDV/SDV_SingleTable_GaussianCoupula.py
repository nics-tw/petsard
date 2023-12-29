from .SDV_SingleTable import SDV_SingleTable

class SDV_SingleTable_GaussianCoupula(SDV_SingleTable):
    def __init__(self,   data, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method = 'GaussianCoupula'

        # metadata already create in SDV_SingleTable
        from sdv.single_table import GaussianCopulaSynthesizer
        self._Synthesizer = GaussianCopulaSynthesizer(self.metadata)