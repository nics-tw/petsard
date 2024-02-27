import pandas as pd

from PETsARD.loader import Loader, Splitter
from PETsARD.processor import Processor
from PETsARD.synthesizer import Synthesizer
from PETsARD.evaluator import Evaluator
from PETsARD.error import ConfigError


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
        self.input: dict = {}
        if config is None:
            raise ConfigError
        pass

    def run(self, input: dict):
        """
        Execute the module's functionality.

        Args:
            input (dict): A input dictionary contains module required input from Status.
                See self.set_input() for more details.
        """
        raise NotImplementedError

    def set_input(self, status) -> dict:
        """
        Set the input for the module.

        Args:
            status (Status): The current status object.
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

    def run(self, input: dict):
        """
        Executes the data loading process using the Loader instance.

        Args:
            input (dict): Loader input should contains nothing ({}).

        Attributes:
            loader.data (pd.DataFrame):
                An loading result data.
        """
        self.loader.load()

    def set_input(self, status) -> dict:
        """
        Sets the input for the LoaderOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict: An empty dictionary.
        """
        return self.input

    def get_result(self):
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
            input (dict):
                Splitter input should contains data (pd.DataFrame) and exclude_index (list).

        Attributes:
            splitter.data (Dict[int, Dict[str, pd.DataFrame]]):
                An splitting result data.
                    First layer is the splitting index, key as int, value as dictionary.
                    Second layer is the splitting result of specific splitting,
                    key as str: 'train' and 'validation', value as pd.DataFrame.
        """
        self.splitter.split(**input)

    def set_input(self, status) -> dict:
        """
        Sets the input for the LoaderOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict: Splitter input should contains data (pd.DataFrame) and exclude_index (list).
        """
        try:
            self.input['data'] = status.get_result('Loader') # Splitter accept Loader only
            self.input['exclude_index'] = status.get_exist_index()
        except:
            raise ConfigError

        return self.input


    def get_result(self):
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
        self.processor = None
        self._config = {} if config['method'].lower() == 'default' else config

    def run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Args:
            input (dict):
                Preprocessor input should contains data (pd.DataFrame) and metadata (Metadata).

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.

        TODO consider use update_config() when #247 is done
        """

        self.processor = Processor(
            metadata=input['metadata']
        )
        # for keep default but update manual only
        self.processor.update_config(self._config)
        self.processor.fit(data=input['data'])
        self.data_preproc = self.processor.transform(data=input['data'])

    def set_input(self, status) -> dict:
        """
        Sets the input for the LoaderOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Preprocessor input should contains data (pd.DataFrame) and metadata (Metadata).
        """
        try:
            if status.pre_module == 'Splitter':
                self.input['data'] = status.get_result(status.pre_module)['train']
            else:  # Loader only
                self.input['data'] = status.get_result(status.pre_module)
            self.input['metadata'] = status.get_metadata()
        except:
            raise ConfigError

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        return self.data_preproc


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

    def set_input(self, status) -> dict:
        """
        Sets the input for the LoaderOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Synthesizer input should contains data (pd.DataFrame).
        """
        try:
            self.input['data'] = status.get_result(status.pre_module)
        except:
            raise ConfigError

        return self.input

    def get_result(self):
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
        self.processor = None
        self._config = {} if config['method'].lower() == 'default' else config

    def run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Args:
            input (dict):
                Postprocessor input should contains data (pd.DataFrame) and preprocessor (Processor).

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """
        self.processor = input['preprocessor']
        self.data_postproc = self.processor.inverse_transform(data=input['data'])

    def set_input(self, status) -> dict:
        """
        Sets the input for the LoaderOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Postprocessor input should contains data (pd.DataFrame) and preprocessor (Processor).
        """
        try:
            self.input['data'] = status.get_result(status.pre_module)
            self.input['preprocessor'] = status.get_processor()
        except:
            raise ConfigError

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        self.data_postproc


class EvaluatorOperator(Operator):
    """
    EvaluatorOperator is responsible for evaluating data
        using the configured Evaluator instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Attributes:
            evaluator (Evaluator):
                An instance of the Evaluator class initialized with the provided configuration.
        """
        super().__init__(config)
        self.evaluator = Evaluator(**config)

    def run(self, input: dict):
        """
        Executes the data synthesizing using the Evaluator instance.

        Args:
            input (dict): Evaluator input should contains data (dict).

        Attributes:
            evaluator.data_syn (pd.DataFrame): An synthesizing result data.
        """
        self.evaluator.create(**input)
        self.evaluator.eval()

    def set_input(self, status) -> dict:
        """
        Sets the input for the LoaderOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Evaluator input should contains data (dict).
        """
        try:
            if 'Splitter' in status.status:
                self.input['data'] = {
                    'ori':     status.get_result('Splitter')['train'],
                    'syn':     status.get_result(status.pre_module),
                    'control': status.get_result('Splitter')['validation']
                }
            else:  # Loader only
                self.input['data'] = {
                    'ori': status.get_result('Loader'),
                    'syn': status.get_result(status.pre_module),
                }
        except:
            raise ConfigError

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        return self.evaluator.evaluation
