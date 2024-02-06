import pandas as pd

from PETsARD.loader import Loader


class Operator:
    """
    Operator is the parent class for every module's decorator:
        {module_name}Operato,
        unifying the method name as .run(), and .get_result().
    """
    def __init__(self, config: dict):
        pass

    def run(self):
        """
        Execute the module's functionality.
        """
        raise NotImplementedError

    def get_result(self, tag: str = None):
        """
        Retrieve the result of the module's operation,
            as data storage varies between modules.
        ...
        Args
            tag (str)
                tag will specifiy some Operator return result.
        """
        raise NotImplementedError


class LoaderOperator(Operator):
    """
    LoaderOperator is responsible for loading data using the configured Loader instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict):
                A dictionary containing configuration parameters for the Loader.
        ...
        Attributes:
            loader (Loader):
                An instance of the Loader class initialized with the provided configuration.
        """
        super().__init__(config)
        self.loader = Loader(**config)

    def run(self):
        """
        Executes the data loading process using the Loader instance.
        """
        self.loader.load()

    def get_result(self, tag: str=None) -> pd.DataFrame:
        """
        Retrieve the loading result.
        ...
        Args
            tag (str)
                Inherited from Operator. Not applicable.
        """
        return self.loader.data