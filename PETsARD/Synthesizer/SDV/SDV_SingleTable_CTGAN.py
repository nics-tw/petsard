import pandas as pd
from sdv.single_table import CTGANSynthesizer

from .SDV_SingleTable import SDV_SingleTable


class SDV_SingleTable_CTGAN(SDV_SingleTable):
    def __init__(self,   data, **kwargs):
        super().__init__(data, **kwargs)

        self.syn_method: str = 'CTGAN'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = CTGANSynthesizer(self.metadata)
