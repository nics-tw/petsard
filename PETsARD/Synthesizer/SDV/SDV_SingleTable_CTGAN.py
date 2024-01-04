from .SDV_SingleTable import SDV_SingleTable
from sdv.single_table import CTGANSynthesizer
import pandas as pd


class SDV_SingleTable_CTGAN(SDV_SingleTable):
    """
    Implement CTGAN synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.

    Return:
        None
    """
    def __init__(self, data: pd.DataFrame, **kwargs):
        super().__init__(data, **kwargs)
        self._syn_method: str = 'CTGAN'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = CTGANSynthesizer(self.metadata)
