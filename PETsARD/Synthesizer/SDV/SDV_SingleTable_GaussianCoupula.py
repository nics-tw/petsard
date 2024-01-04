from .SDV_SingleTable import SDV_SingleTable
from sdv.single_table import GaussianCopulaSynthesizer
import pandas as pd


class SDV_SingleTable_GaussianCoupula(SDV_SingleTable):
    def __init__(self, data: pd.DataFrame, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method = 'GaussianCoupula'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = GaussianCopulaSynthesizer(self.metadata)
