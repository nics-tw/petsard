from .SDV_SingleTable import SDV_SingleTable
from sdv.single_table import CopulaGANSynthesizer
import pandas as pd


class SDV_SingleTable_CoupulaGAN(SDV_SingleTable):
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
        self._syn_method: str = 'CoupulaGAN'

        # metadata already create in SDV_SingleTable
        self._Synthesizer = CopulaGANSynthesizer(self.metadata)
