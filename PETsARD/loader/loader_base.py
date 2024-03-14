from abc import ABC, abstractmethod


class LoaderBase(ABC):
    """
    LoaderBase
        Base class for all "Loader".

        The "Loader" class defines the common API
        that all the "Loader" need to implement, as well as common functionality.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration for the loader modules.

        Attr:
            config (dict): The configuration for the loader modules.
        """
        self.config = config

    @abstractmethod
    def load(self):
        """
        Load and return the data
        """
        raise NotImplementedError()
