from .SDV_SingleTable_CoupulaGAN import SDV_SingleTable_CoupulaGAN
from .SDV_SingleTable_CTGAN import SDV_SingleTable_CTGAN
from .SDV_SingleTable_GaussianCoupula import SDV_SingleTable_GaussianCoupula
from .SDV_SingleTable_TVAE import SDV_SingleTable_TVAE
import pandas as pd


class SDV_SingleTableFactory:
    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Base class for all "SDV".

        The "SDV" class defines the common API
        that all the "SDV" need to implement, as well as common functionality.

        Args:
            data (pd.DataFrame): The data to be synthesized.
            **kwargs: The other parameters.

        Return:
            None
        """
        synthesizing_method = kwargs.get('synthesizing_method', None)
        # _para = {
        #     'sample_num_rows': kwargs.get('sample_num_rows', None)
        #    ,'sample_batch_size': kwargs.get('sample_batch_size', None)
        # }
        #  ,**_para

        if synthesizing_method == 'sdv-singletable-coupulagan':
            _Synthesizer = SDV_SingleTable_CoupulaGAN(data=data)

        elif synthesizing_method == 'sdv-singletable-ctgan':
            _Synthesizer = SDV_SingleTable_CTGAN(data=data)

        elif synthesizing_method == 'sdv-singletable-gaussiancoupula':
            _Synthesizer = SDV_SingleTable_GaussianCoupula(data=data)
            
        elif synthesizing_method == 'sdv-singletable-tvae':
            _Synthesizer = SDV_SingleTable_TVAE(data=data)

        else:
            raise ValueError(
                f"Synthesizer (SDV - SDV_SingleTableFactory): synthesizing_method {synthesizing_method} didn't support.")

        self.Synthesizer = _Synthesizer

    def create_synthesizer(self):
        """
        Create synthesizer instance.

        Args:
            None

        Return:
            self.Synthesizer (synthesizer): The synthesizer instance.
        """
        return self.Synthesizer
