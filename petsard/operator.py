import functools
import logging
import time
from copy import deepcopy
from datetime import timedelta

import pandas as pd

from petsard.constrainer import Constrainer
from petsard.evaluator import Describer, Evaluator
from petsard.exceptions import ConfigError
from petsard.loader import Loader, Splitter
from petsard.metadater import SchemaMetadata
from petsard.processor import Processor
from petsard.reporter import Reporter
from petsard.synthesizer import Synthesizer


class BaseOperator:
    """
    The interface of the objects used by Executor.run()
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict):
                A dictionary containing configuration parameters.

        Attr.:
            module_name (str):
                The name of the module.
            logger (logging.Logger):
                The logger object for the module.
            config (dict):
                The configuration parameters for the module.
            input (dict):
                The input data for the module.
        """
        self.module_name: str = self.__class__.__name__.replace("Operator", "Op")
        self._logger = logging.getLogger(f"PETsARD.{self.module_name}")

        self.config = config
        self.input: dict = {}
        if config is None:
            self._logger.error("Configuration is None")
            self._logger.debug("Error details: ", exc_info=True)
            raise ConfigError

    def run(self, input: dict):
        """
        Execute the module's functionality.

        Args:
            input (dict): A input dictionary contains module required input from Status.
                See self.set_input() for more details.
        """
        start_time: time = time.time()
        self._logger.info(f"TIMING_START|{self.module_name}|run|{start_time}")
        self._logger.info(f"Starting {self.module_name} execution")

        try:
            self._run(input)

            elapsed_time: time = time.time() - start_time
            formatted_elapsed_time: str = str(timedelta(seconds=round(elapsed_time)))

            self._logger.info(
                f"TIMING_END|{self.module_name}|run|{time.time()}|{elapsed_time}"
            )
            self._logger.info(
                f"Completed {self.module_name} execution "
                f"(elapsed: {formatted_elapsed_time})"
            )
        except Exception as e:
            elapsed_time: time = time.time() - start_time
            self._logger.error(
                f"TIMING_ERROR|{self.module_name}|run|{time.time()}|{elapsed_time}|{str(e)}"
            )
            raise

    @classmethod
    def log_and_raise_config_error(cls, func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self._logger.error(f"Configuration error in {func.__name__}: {str(e)}")
                self._logger.debug("Error details: ", exc_info=True)
                raise ConfigError(f"Config error in {func.__name__}: {str(e)}")

        return wrapper

    @staticmethod
    def log_and_raise_not_implemented(func):
        """Decorator for handling not implemented methods"""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except NotImplementedError:
                self._logger.error(
                    f"Method {func.__name__} not implemented in {self.module_name}"
                )
                raise NotImplementedError(
                    f"Method {func.__name__} must be implemented in {self.module_name}"
                )

        return wrapper

    @log_and_raise_not_implemented
    def _run(self, input: dict):
        """
        Execute the module's functionality.

        Args:
            input (dict): A input dictionary contains module required input from Status.
                See self.set_input() for more details.
        """
        raise NotImplementedError

    @log_and_raise_not_implemented
    def set_input(self, status) -> dict:
        """
        Set the input for the module.

        Args:
            status (Status): The current status object.
        """
        raise NotImplementedError

    @log_and_raise_not_implemented
    def get_result(self):
        """
        Retrieve the result of the module's operation,
            as data storage varies between modules.
        """
        raise NotImplementedError

    @log_and_raise_not_implemented
    def get_metadata(self) -> SchemaMetadata:
        """
        Retrieve the metadata of the loaded data.

        Returns:
            (SchemaMetadata): The metadata of the loaded data.
        """
        raise NotImplementedError


class LoaderOperator(BaseOperator):
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
        self._schema_metadata = None  # Store the SchemaMetadata

    def _run(self, input: dict):
        """
        Executes the data loading process using the Loader instance.

        Args:
            input (dict): Loader input should contains nothing ({}).

        Attributes:
            loader.data (pd.DataFrame):
                An loading result data.
        """
        self._logger.debug("Starting data loading process")
        self.data, self._schema_metadata = self.loader.load()

        # Use SchemaMetadata directly
        self._logger.debug("Using SchemaMetadata from Metadater")
        self.metadata = self._schema_metadata

        self._logger.debug("Data loading completed")

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
        return self.data

    def get_metadata(self) -> SchemaMetadata:
        """
        Retrieve the metadata of the loaded data.

        Returns:
            (SchemaMetadata): The metadata of the loaded data.
        """
        return self.metadata


class SplitterOperator(BaseOperator):
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

    def _run(self, input: dict):
        """
        Executes the data splitting process using the Splitter instance.

        Args:
            input (dict):
                Splitter input should contains data (pd.DataFrame) and exclude_index (list[set]).

        Attributes:
            data (Dict[int, Dict[str, pd.DataFrame]]):
                An splitting result data.
                    First layer is the splitting index, key as int, value as dictionary.
                    Second layer is the splitting result of specific splitting,
                    key as str: 'train' and 'validation', value as pd.DataFrame.
            train_indices (Dict[int, List[int]]):
                The original indices of training data for each sample.
        """
        self._logger.debug("Starting data splitting process")
        # Only pass parameters that Splitter.split() accepts and are not empty
        split_params = {}
        for key, value in input.items():
            if key == "data":
                split_params[key] = value
            elif key == "exist_train_indices" and value:  # 只有非空時才傳遞
                split_params[key] = value
        self.data, self.metadata, self.train_indices = self.splitter.split(
            **split_params
        )
        self._logger.debug("Data splitting completed")

    @BaseOperator.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the SplitterOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict: Splitter input should contains
                data (pd.DataFrame), exclude_index (list), and Metadata (Metadata)
        """
        if "method" in self.config:
            # Splitter method = 'custom_data'
            self.input["data"] = None
        else:
            # Splitter accept following Loader only
            self.input["data"] = status.get_result("Loader")
            self.input["metadata"] = status.get_metadata("Loader")
        self.input["exist_train_indices"] = status.get_exist_train_indices()

        return self.input

    def get_result(self):
        """
        Retrieve the splitting result.
            Due to Config force num_samples = 1, return 1st dataset is fine.
        """
        result: dict = deepcopy(self.data[1])
        return result

    def get_metadata(self) -> SchemaMetadata:
        """
        Retrieve the metadata.

        Returns:
            (SchemaMetadata): The updated metadata.
        """
        return deepcopy(self.metadata[1]["train"])

    def get_train_indices(self) -> list[set]:
        """
        Retrieve the training indices for each sample.

        Returns:
            list[set]: Training indices as list of sets
        """
        return deepcopy(self.train_indices)


class PreprocessorOperator(BaseOperator):
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
            _config (dict): The configuration parameters for the Processor.
            _sequence (list): The sequence of the pre-processing steps (if any
        """
        super().__init__(config)
        self.processor = None
        method = config["method"].lower() if "method" in config else "custom"
        self._sequence = None
        if "sequence" in config:
            self._sequence = config["sequence"]

        # Extract the processor configuration properly
        if method == "default":
            self._config = {}
        else:
            # For custom method, extract the "config" key if it exists
            # Otherwise use the config directly (for backward compatibility)
            if "config" in config:
                self._config = config["config"]
            else:
                # Remove non-processor keys from config
                self._config = {
                    k: v for k, v in config.items() if k not in ["method", "sequence"]
                }

    def _run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Args:
            input (dict):
                Preprocessor input should contains data (pd.DataFrame) and metadata (Metadata).

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """

        self._logger.debug("Initializing processor")
        self.processor = Processor(metadata=input["metadata"], config=self._config)

        if self._sequence is None:
            self._logger.debug("Using default processing sequence")
            self.processor.fit(data=input["data"])
        else:
            self._logger.debug(f"Using custom sequence: {self._sequence}")
            self.processor.fit(data=input["data"], sequence=self._sequence)

        self._logger.debug("Transforming data")
        self.data_preproc = self.processor.transform(data=input["data"])

    @BaseOperator.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the PreprocessorOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Preprocessor input should contains
                    data (pd.DataFrame) and metadata (Metadata).
        """
        pre_module = status.get_pre_module("Preprocessor")
        if pre_module == "Splitter":
            self.input["data"] = status.get_result(pre_module)["train"]
        else:  # Loader only
            self.input["data"] = status.get_result(pre_module)
        self.input["metadata"] = status.get_metadata(pre_module)

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        result: pd.DataFrame = deepcopy(self.data_preproc)
        return result

    def get_metadata(self) -> SchemaMetadata:
        """
        Retrieve the metadata.
            If the encoder is EncoderUniform,
            update the metadata infer_dtype to numerical.

        Returns:
            (SchemaMetadata): The updated metadata.
        """
        metadata: SchemaMetadata = deepcopy(self.processor._metadata)

        # Note: The metadata update logic for EncoderUniform and ScalerTimeAnchor
        # needs to be adapted to work with SchemaMetadata instead of legacy Metadata
        # This will be handled by the processor module's own refactoring

        return metadata


class SynthesizerOperator(BaseOperator):
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

        self.synthesizer: Synthesizer = Synthesizer(**config)
        self.data_syn: pd.DataFrame = None

    def _run(self, input: dict):
        """
        Executes the data synthesizing using the Synthesizer instance.

        Args:
            input (dict): Synthesizer input should contains data (pd.DataFrame).

        Attributes:
            synthesizer.data_syn (pd.DataFrame):
                An synthesizing result data.
        """
        self._logger.debug("Starting data synthesizing process")

        self.synthesizer.create(metadata=input["metadata"])
        self._logger.debug("Synthesizing model initialization completed")

        self.data_syn = self.synthesizer.fit_sample(data=input["data"])
        self._logger.debug("Train and sampling Synthesizing model completed")

    @BaseOperator.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the SynthesizerOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Synthesizer input should contains data (pd.DataFrame)
                    and SDV format metadata (dict or None).
        """
        pre_module = status.get_pre_module("Synthesizer")

        # Check if metadata exists for the previous module
        try:
            self.input["metadata"] = status.get_metadata(pre_module)
            # Validate that the metadata has fields
            if not self.input["metadata"].fields:
                self._logger.warning(
                    f"Metadata from {pre_module} has no fields, setting to None"
                )
                self.input["metadata"] = None
        except Exception as e:
            self._logger.warning(f"Could not get metadata from {pre_module}: {e}")
            self.input["metadata"] = None

        if pre_module == "Splitter":
            self.input["data"] = status.get_result(pre_module)["train"]
        else:  # Loader or Preprocessor
            self.input["data"] = status.get_result(pre_module)

        return self.input

    def get_result(self):
        """
        Retrieve the synthesizing result.
        """
        return deepcopy(self.data_syn)


class PostprocessorOperator(BaseOperator):
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
        self._config = {} if config["method"].lower() == "default" else config

    def _run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Args:
            input (dict):
                Postprocessor input should contains data (pd.DataFrame) and preprocessor (Processor).

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """
        self._logger.debug("Starting data postprocessing process")

        self.processor = input["preprocessor"]
        self._logger.debug("Processor configuration loading completed")

        self.data_postproc = self.processor.inverse_transform(data=input["data"])
        self._logger.debug("Data postprocessing completed")

    @BaseOperator.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the PostprocessorOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Postprocessor input should contains data (pd.DataFrame) and preprocessor (Processor).
        """
        self.input["data"] = status.get_result(status.get_pre_module("Postprocessor"))
        self.input["preprocessor"] = status.get_processor()

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        result: pd.DataFrame = deepcopy(self.data_postproc)
        return result


class ConstrainerOperator(BaseOperator):
    """
    ConstrainerOperator is responsible for applying constraints to data
    using the configured Constrainer instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Initialize ConstrainerOperator with given configuration.

        Args:
            config (dict): Configuration parameters for the Constrainer.

        Attributes:
            constrainer (Constrainer): An instance of the Constrainer class
                initialized with the provided configuration.
        """
        # Transform field combinations before initializing
        config = self._transform_field_combinations(config)
        super().__init__(config)

        # Store sampling configuration if provided
        self.sample_dict = {}
        self.sample_dict.update(
            {
                key: config.pop(key)
                for key in [
                    "target_rows",
                    "sampling_ratio",
                    "max_trials",
                    "verbose_step",
                ]
                if key in config
            }
        )

        self.constrainer = Constrainer(config)

    def _run(self, input: dict):
        """
        Execute data constraining process using the Constrainer instance.

        Args:
            input (dict): Constrainer input should contain:
                - data (pd.DataFrame): Data to be constrained
                - synthesizer (optional): Synthesizer instance if resampling is needed
                - postprocessor (optional): Postprocessor instance if needed

        Attributes:
            constrained_data (pd.DataFrame): The constrained result data.
        """
        self._logger.debug("Starting data constraining process")

        if "target_rows" not in self.sample_dict:
            self.sample_dict["target_rows"] = len(input["data"])

        if "synthesizer" in input:
            # Use resample_until_satisfy if sampling parameters and synthesizer are provided
            self._logger.debug("Using resample_until_satisfy method")
            self.constrained_data = self.constrainer.resample_until_satisfy(
                data=input["data"],
                synthesizer=input["synthesizer"],
                postprocessor=input.get("postprocessor"),
                **self.sample_dict,
            )
        else:
            # Use simple apply method
            self._logger.debug("Using apply method")
            self.constrained_data = self.constrainer.apply(input["data"])

        self._logger.debug("Data constraining completed")

    @BaseOperator.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Set the input for the ConstrainerOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict: Constrainer input should contain:
                - data (pd.DataFrame)
                - synthesizer (optional)
                - postprocessor (optional)
        """
        pre_module = status.get_pre_module("Constrainer")

        # Get data from previous module
        if pre_module == "Splitter":
            self.input["data"] = status.get_result(pre_module)["train"]
        else:  # Loader, Preprocessor, Synthesizer, or Postprocessor
            self.input["data"] = status.get_result(pre_module)

        # Get synthesizer if available
        if "Synthesizer" in status.status:
            self.input["synthesizer"] = status.get_synthesizer()

        # Get postprocessor if available
        if "Postprocessor" in status.status:
            self.input["postprocessor"] = status.get_processor()

        return self.input

    def get_result(self):
        """
        Retrieve the constraining result.

        Returns:
            pd.DataFrame: The constrained data.
        """
        return deepcopy(self.constrained_data)

    def _transform_field_combinations(self, config: dict) -> dict:
        """Transform field combinations from YAML list format to tuple format

        Args:
            config: Original config dictionary

        Returns:
            Updated config with transformed field_combinations
        """
        if "field_combinations" in config:
            # Deep copy to avoid modifying original config
            config = deepcopy(config)
            # Transform each combination from [dict, dict] to tuple(dict, dict)
            config["field_combinations"] = [
                tuple(combination) for combination in config["field_combinations"]
            ]
        return config


class EvaluatorOperator(BaseOperator):
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
        self.evaluations: dict[str, pd.DataFrame] = None

    def _run(self, input: dict):
        """
        Executes the data evaluating using the Evaluator instance.

        Args:
            input (dict): Evaluator input should contains data (dict).

        Attributes:
            evaluator.result (dict): An evaluating result data.
        """
        self._logger.debug("Starting data evaluating process")

        self.evaluator.create()
        self._logger.debug("Evaluation model initialization completed")

        self.evaluations = self.evaluator.eval(**input)
        self._logger.debug("Data evaluating completed")

    @BaseOperator.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the EvaluatorOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Evaluator input should contains data (dict).
        """
        if "Splitter" in status.status:
            self.input["data"] = {
                "ori": status.get_result("Splitter")["train"],
                "syn": status.get_result(status.get_pre_module("Evaluator")),
                "control": status.get_result("Splitter")["validation"],
            }
        else:  # Loader only
            self.input["data"] = {
                "ori": status.get_result("Loader"),
                "syn": status.get_result(status.get_pre_module("Evaluator")),
            }

        return self.input

    def get_result(self) -> dict[str, pd.DataFrame]:
        """
        Retrieve the pre-processing result.

        Returns:
            (dict[str, pd.DataFrame]): The evaluation results.
        """
        return deepcopy(self.evaluations)


class DescriberOperator(BaseOperator):
    """
    DescriberOperator is responsible for describing data
        using the configured Describer instance as a decorator.
    """

    INPUT_PRIORITY: list[str] = [
        "Postprocessor",
        "Synthesizer",
        "Preprocessor",
        "Splitter",
        "Loader",
    ]

    def __init__(self, config: dict):
        """
        Attributes:
            describer (Describer):
                An instance of the Describer class initialized with the provided configuration.
        """
        super().__init__(config)
        self.describer = Describer(**config)
        self.description: dict[str, pd.DataFrame] = None

    def _run(self, input: dict):
        """
        Executes the data describing using the Describer instance.

        Args:
            input (dict): Describer input should contains data (dict).

        Attributes:
            describer.result (dict): An describing result data.
        """
        self._logger.debug("Starting data describing process")

        self.describer.create()
        self._logger.debug("Describing model initialization completed")

        self.description = self.describer.eval(**input)
        self._logger.debug("Data describing completed")

    @BaseOperator.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the DescriberOperator.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Describer input should contains data (dict).
        """

        self.input["data"] = None
        for module in self.INPUT_PRIORITY:
            if module in status.status:
                self.input["data"] = {
                    "data": (
                        status.get_result("Splitter")["train"]
                        if module == "Splitter"
                        else status.get_result(module)
                    )
                }
                break

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        return deepcopy(self.description)


class ReporterOperator(BaseOperator):
    """
    Operator class for generating reports using the Reporter class.

    Args:
        config (dict): Configuration parameters for the Reporter.

    Attributes:
        reporter (Reporter): Instance of the Reporter class.
        report (dict): Dictionary to store the generated reports.

    Methods:
        _run(input: dict): Runs the Reporter to create and generate reports.
        set_input(status) -> dict: Sets the input data for the Reporter.
        get_result(): Placeholder method for getting the result.

    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.reporter = Reporter(**config)
        self.report: dict = {}

    def _run(self, input: dict):
        """
        Runs the Reporter to create and generate reports.

        Args:
            input (dict): Input data for the Reporter.
                - data (dict): The data to be reported.
        """
        self._logger.debug("Starting data reporting process")

        temp: dict = None
        eval_expt_name: str = None
        report: pd.DataFrame = None
        self.reporter.create(data=input["data"])
        self._logger.debug("Reporting configuration initialization completed")

        self.reporter.report()
        if "Reporter" in self.reporter.result:
            # ReporterSaveReport
            temp = self.reporter.result["Reporter"]
            # exception handler so no need to collect exist report in this round
            #   e.g. no matched granularity
            if "warnings" in temp:
                return
            if not all(key in temp for key in ["eval_expt_name", "report"]):
                raise ConfigError
            eval_expt_name = temp["eval_expt_name"]
            report = deepcopy(temp["report"])
            self.report[eval_expt_name] = report
        else:
            # ReporterSaveData
            self.report = self.reporter.result
        self._logger.debug("Data reporting completed")

    def set_input(self, status) -> dict:
        """
        Sets the input data for the Reporter.

        Args:
            status: The status object.

        Returns:
            dict: The input data for the Reporter.
        """
        full_expt = status.get_full_expt()

        data = {}
        for module in full_expt.keys():
            index_dict = status.get_full_expt(module=module)
            result = status.get_result(module=module)

            # if module.get_result is a dict,
            #   add key into expt_name: expt_name[key]
            if isinstance(result, dict):
                for key in result.keys():
                    temp_dict: dict = index_dict.copy()
                    temp_dict[module] = f"{index_dict[module]}_[{key}]"
                    index_tuple = tuple(
                        item for pair in temp_dict.items() for item in pair
                    )
                    data[index_tuple] = deepcopy(result[key])
            else:
                index_tuple = tuple(
                    item for pair in index_dict.items() for item in pair
                )
                data[index_tuple] = deepcopy(result)
        self.input["data"] = data
        self.input["data"]["exist_report"] = status.get_report()

        # 新增時間資料支援
        if hasattr(status, "get_timing_report_data"):
            timing_data = status.get_timing_report_data()
            if not timing_data.empty:
                self.input["data"]["timing_data"] = timing_data

        return self.input

    def get_result(self):
        """
        Placeholder method for getting the result.

        Returns:
            (dict) key as module name,
            value as raw/processed data (others) or report data (Reporter)
        """
        return deepcopy(self.report)
