import pandas as pd

from .SDV_SingleTable_CopulaGAN import SDV_SingleTable_CopulaGAN
from .SDV_SingleTable_CTGAN import SDV_SingleTable_CTGAN
from .SDV_SingleTable_GaussianCopula import SDV_SingleTable_GaussianCopula
from .SDV_SingleTable_TVAE import SDV_SingleTable_TVAE


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

        TODO As AnonymeterMethodMap, use class define mapping of string and int,
             don't use string condition.
        """
        synthesizing_method: str = kwargs.get('synthesizing_method', None)

        if synthesizing_method == 'sdv-singletable-copulagan':
            self.Synthesizer = SDV_SingleTable_CopulaGAN(data=data)
        elif synthesizing_method == 'sdv-singletable-ctgan':
            self.Synthesizer = SDV_SingleTable_CTGAN(data=data)
        elif synthesizing_method == 'sdv-singletable-gaussiancopula':
            self.Synthesizer = SDV_SingleTable_GaussianCopula(data=data)
        elif synthesizing_method == 'sdv-singletable-tvae':
            self.Synthesizer = SDV_SingleTable_TVAE(data=data)

        else:
            raise ValueError(
                f"Synthesizer (SDV - SDV_SingleTableFactory): "
                f"synthesizing_method {synthesizing_method} didn't support."
            )

    def create_synthesizer(self):
        """
        Create synthesizer instance.

        Args:
            None

        Return:
            self.Synthesizer (synthesizer): The synthesizer instance.
        """
        return self.Synthesizer
