import pandas as pd
from sdv.single_table import GaussianCopulaSynthesizer

from PETsARD.Synthesizer.SDV.SDV_SingleTable import SDV_SingleTable


class SDV_SingleTable_GaussianCopula(SDV_SingleTable):
    """
    Implement Gaussian Copula synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.

    Return:
        None
    """

    def __init__(self, data: pd.DataFrame, **kwargs):
        super().__init__(data, **kwargs)
        self.syn_method: str = 'GaussianCopula'

        self._Synthesizer = GaussianCopulaSynthesizer(self.metadata)
