import pandas as pd
from sdv.single_table import TVAESynthesizer

from .SDV_SingleTable import SDV_SingleTable
from sdv.single_table import TVAESynthesizer
import pandas as pd


class SDV_SingleTable_TVAE(SDV_SingleTable):
    def __init__(self,   data, **kwargs):
        super().__init__(data, **kwargs)
        self.syn_method: str = 'TVAE'
        self._syn_method: str = 'TVAE'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = TVAESynthesizer(self.metadata)
