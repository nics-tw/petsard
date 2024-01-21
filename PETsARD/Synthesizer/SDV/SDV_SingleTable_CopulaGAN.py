import pandas as pd
from sdv.single_table import CopulaGANSynthesizer

from PETsARD.Synthesizer.SDV.SDV_SingleTable import SDV_SingleTable


class SDV_SingleTable_CopulaGAN(SDV_SingleTable):
    """
    Implement CopulaGAN synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.

    Return:
        None
    """

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        super().__init__(data, **kwargs)
        self.syn_method: str = 'CopulaGAN'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = CopulaGANSynthesizer(self.metadata)
