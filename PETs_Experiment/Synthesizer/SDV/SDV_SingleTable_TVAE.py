from .SDV_SingleTable import SDV_SingleTable

class SDV_SingleTable_TVAE(SDV_SingleTable):
    def __init__(self,   data, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method = 'TVAE'

        # metadata already create in SDV_SingleTable
        from sdv.single_table import TVAESynthesizer
        self._Synthesizer = TVAESynthesizer(self.metadata)