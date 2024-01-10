import pandas as pd
from sdv.single_table import TVAESynthesizer

from PETsARD.Synthesizer.SDV.SDV_SingleTable import SDV_SingleTable


class SDV_SingleTable_TVAE(SDV_SingleTable):
    """
    Implement TVAE synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.

    Return:
        None
    """

    def __init__(self, data: pd.DataFrame, **kwargs):
        super().__init__(data, **kwargs)
        self.syn_method: str = 'TVAE'

        self._Synthesizer = TVAESynthesizer(self.metadata)
