import pandas as pd

from PETsARD.loader import Loader, Splitter
from PETsARD.processor import Processor
from PETsARD.synthesizer import Synthesizer


class Operator:
    """
    The interface of the objects used by Executor.run()
    """
    def __init__(self, config: dict):
        """
        Args:
            config (dict):
                A dictionary containing configuration parameters.
        """
        pass

    def run(self, input: dict):
        """
        Execute the module's functionality.

        Args:
            input (dict):
                A input dictionary contains module required input from Status.
                See Status.get_input_from_prev(module) for more details.
        """
        raise NotImplementedError

    def get_result(self):
        """
        Retrieve the result of the module's operation,
            as data storage varies between modules.

        Args
            tag (str):
                Specify (return) items of result.
        """
        raise NotImplementedError


class LoaderOperator(Operator):
    """
    LoaderOperator is responsible for loading data using the configured Loader instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Loader.

        Attributes:
            loader (Loader):
                An instance of the Loader class initialized with the provided configuration.
        """
        super().__init__(config)
        self.loader = Loader(**config)

    def run(self, input: dict=None):
        """
        Executes the data loading process using the Loader instance.

        Args:
            input (dict): Loader input should contains nothing ({}).

        Attributes:
            loader.data (pd.DataFrame):
                An loading result data.
        """
        self.loader.load()

    def get_result(self) -> pd.DataFrame:
        """
        Retrieve the loading result.
        """
        return self.loader.data
    

class SplitterOperator(Operator):
    """
    SplitterOperator is responsible for splitting data
        using the configured Loader instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Splitter.

        Attributes:
            splitter (Splitter):
                An instance of the Splitter class initialized with the provided configuration.
        """
        super().__init__(config)
        self.splitter = Splitter(**config)

    def run(self, input: dict):
        """
        Executes the data splitting process using the Splitter instance.

        Args:
            input (dict): Splitter input should contains data (pd.DataFrame) and exclude_index (list).

        Attributes:
            splitter.data (Dict[int, Dict[str, pd.DataFrame]]):
                An splitting result data.
                    First layer is the splitting index, key as int, value as dictionary.
                    Second layer is the splitting result of specific splitting,
                    key as str: 'train' and 'validation', value as pd.DataFrame.
        """
        self.splitter.split(**input)

    def get_result(self) -> pd.DataFrame:
        """
        Retrieve the splitting result.
            Due to Config force num_samples = 1, return 1st dataset is fine.
        """
        return self.splitter.data[1]


class PreprocessorOperator(Operator):
    """
    PreprocessorOperator is responsible for pre-processing data
        using the configured Processor instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Processor.

        Attributes:
            _processor (Processor): The processor object used by the Operator.
            _config (dict): The configuration parameters for the Operator.
        """
        super().__init__(config)
        self._processor = None
        self._config = config

    def run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """
        self._processor = Processor(
            metadata=input['metadata'],
            config=self._config
        )
        self._processor.fit(**input)
        self._processor.data_preproc: pd.DataFrame = \
            self._processor.transform(**input)

    def get_result(self) -> pd.DataFrame:
        """
        Retrieve the pre-processing result.
        """
        return self.processor.data_preproc


class SynthesizerOperator(Operator):
    """
    SynthesizerOperator is responsible for synthesizing data
        using the configured Synthesizer instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Attributes:
            synthesizer (Synthesizer):
                An instance of the Synthesizer class initialized with the provided configuration.
        """
        super().__init__(config)
        self.synthesizer = Synthesizer(**config)

    def run(self, input: dict):
        """
        Executes the data synthesizing using the Synthesizer instance.

        Args:
            input (dict): Synthesizer input should contains data (pd.DataFrame).

        Attributes:
            synthesizer.data_syn (pd.DataFrame):
                An synthesizing result data.
        """
        self.synthesizer.create(**input)
        self.synthesizer.fit_sample()

    def get_result(self) -> pd.DataFrame:
        """
        Retrieve the synthesizing result.
        """
        return self.synthesizer.data_syn


    

class PostprocessorOperator(Operator):
    """
    PostprocessorOperator is responsible for post-processing data
        using the configured Processor instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Processor.

        Attributes:
            _processor (Processor): The processor object used by the Operator.
            _config (dict): The configuration parameters for the Operator.
        """
        super().__init__(config)
        self._processor = None
        self._config = config

    def run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """
        self._processor = input['preprocessor']
        self._processor.data_postproc: pd.DataFrame = \
            self._processor.inverse_transform(data=input['data'])

    def get_result(self) -> pd.DataFrame:
        """
        Retrieve the pre-processing result.
        """
        return self.processor.data_postproc