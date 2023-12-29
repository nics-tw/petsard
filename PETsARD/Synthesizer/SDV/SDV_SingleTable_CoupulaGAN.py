from .SDV_SingleTable import SDV_SingleTable

class SDV_SingleTable_CoupulaGAN(SDV_SingleTable):
    def __init__(self,   data, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method = 'CoupulaGAN'

        # metadata already create in SDV_SingleTable
        from sdv.single_table import CopulaGANSynthesizer
        self._Synthesizer = CopulaGANSynthesizer(self.metadata)