from .SDV_SingleTable import SDV_SingleTable
from sdv.single_table import CTGANSynthesizer
import pandas as pd


class SDV_SingleTable_CTGAN(SDV_SingleTable):
    def __init__(self, data: pd.DataFrame, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method = 'CTGAN'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = CTGANSynthesizer(self.metadata)
