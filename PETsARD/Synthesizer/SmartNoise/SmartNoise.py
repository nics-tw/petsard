import pandas as pd


class SmartNoise():
    """
    Base class for all "SmartNoise".

    The "SmartNoise" class defines the common API
    that all the "SmartNoise" need to implement, 
    as well as common functionality.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.

    Return:
        None
    """

    def __init__(self, data: pd.DataFrame, **kwargs):
        self.data: pd.DataFrame = data
        self.syn_method: str = 'Unknown'
