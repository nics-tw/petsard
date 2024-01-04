import pandas as pd
from sdv.single_table import CTGANSynthesizer

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

        self.syn_method: str = 'CTGAN'

        self._Synthesizer = CTGANSynthesizer(self.metadata)
