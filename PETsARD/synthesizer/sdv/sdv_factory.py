import pandas as pd

from PETsARD.synthesizer.sdv.sdv_singletable_factory import SDV_SingleTableFactory


class SDVFactory:
    """
    Manage the SDV synthesizers.
    It allocates the task to the right SDV synthesizer based on the parameters.

    Args:
        data (pd.DataFrame): The data to be synthesized from.
        **kwargs: The other parameters.

    Return:
        None

    TODO As AnonymeterMethodMap, use class define mapping of string and int,
         don't use string condition.
    """

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        synthesizing_method: str = kwargs.get('synthesizing_method', None)

        if synthesizing_method.startswith('sdv-singletable'):
            self.Synthesizer = SDV_SingleTableFactory(
                data=data,
                synthesizing_method=synthesizing_method
            ).create_synthesizer()
        else:
            raise ValueError(
                f"Synthesizer (SDV - SDVFactory): "
                f"synthesizing_method {synthesizing_method} "
                f"didn't support."
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
