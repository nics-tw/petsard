import pandas as pd


class SDV():
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
    def __init__(self, data: pd.DataFrame, **kwargs):
        self.data: pd.DataFrame = data
        pass
