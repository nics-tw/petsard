from abc import ABC, abstractmethod


class LoaderBase(ABC):
    """
    LoaderBase
        Base class for all "Loader".

        The "Loader" class defines the common API
        that all the "Loader" need to implement, as well as common functionality.

    """

    def __init__(self, para_Loader: dict):
        self.para_Loader = para_Loader

    @abstractmethod
    def load(self):
        """
        Load and return the data
        """
        raise NotImplementedError()
