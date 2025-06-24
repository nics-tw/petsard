import queue
import re
from copy import deepcopy
from typing import Tuple, Union

import pandas as pd

from petsard.exceptions import ConfigError, UnexecutedError
from petsard.metadater import SchemaMetadata
from petsard.operator import (  # noqa: F401 - Dynamic Imports
    BaseOperator,
    ConstrainerOperator,
    DescriberOperator,
    EvaluatorOperator,
    LoaderOperator,
    PostprocessorOperator,
    PreprocessorOperator,
    ReporterOperator,
    SplitterOperator,
    SynthesizerOperator,
)
from petsard.processor import Processor
from petsard.synthesizer import Synthesizer


class Config:
    """
    The config of experiment for executor to read.

    Config file should follow specific format:
    ...
    - {module name}
        - {task name}
            - {module parameter}: {value}
    ...
    task name is assigned by user.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
        """
        self.config: queue.Queue = queue.Queue()
        self.module_flow: queue.Queue = queue.Queue()
        self.expt_flow: queue.Queue = queue.Queue()
        self.sequence: list = []
        self.yaml: dict = {}

        # Set executor configuration
        self.yaml = config

        # Set sequence
        self.sequence = list(self.yaml.keys())

        # Config check
        pattern = re.compile(r"_(\[[^\]]*\])$")
        for module, expt_config in self.yaml.items():
            for expt_name in expt_config:
                # any expt_name should not be postfix with "_[xxx]"
                if pattern.search(expt_name):
                    raise ConfigError

        if "Splitter" in self.yaml:
            if "method" not in self.yaml["Splitter"]:
                self.yaml["Splitter"] = self._splitter_handler(
                    deepcopy(self.yaml["Splitter"])
                )

        self.config, self.module_flow, self.expt_flow = self._set_flow()

    def _set_flow(self) -> Tuple[queue.Queue, queue.Queue, queue.Queue]:
        """
        Populate queues with module operators.

        Returns:
            flow (queue.Queue):
                Queue containing the operators in the order they were traversed.
            module_flow (queue.Queue):
                Queue containing the module names corresponding to each operator.
            expt_flow (queue.Queue):
                Queue containing the experiment names corresponding to each operator.
        """
        flow: queue.Queue = queue.Queue()
        module_flow: queue.Queue = queue.Queue()
        expt_flow: queue.Queue = queue.Queue()

        def _set_flow_dfs(modules):
            """
            Depth-First Search (DFS) algorithm
                for traversing the sequence of modules recursively.
            """
            if not modules:
                return

            module = modules[0]
            remaining_modules = modules[1:]

            if module in self.yaml:
                for expt_name, expt_config in self.yaml[module].items():
                    flow.put(eval(f"{module}Operator(expt_config)"))
                    module_flow.put(module)
                    expt_flow.put(expt_name)
                    _set_flow_dfs(remaining_modules)

        _set_flow_dfs(self.sequence)
        return flow, module_flow, expt_flow

    def _splitter_handler(self, config: dict) -> dict:
        """
        Transforms and expands the Splitter configuration for each specified 'num_samples',
            creating unique entries with a new experiment name format '{expt_name}_0n|NN}."

        Args:
            config (dict): The original Splitter configuration.

        Returns:
            (dict): Transformed and expanded configuration dictionary.
        """
        transformed_config: dict = {}
        for expt_name, expt_config in config.items():
            num_samples = expt_config.get("num_samples", 1)
            iter_expt_config = deepcopy(expt_config)
            iter_expt_config["num_samples"] = 1

            num_samples_str = str(num_samples)
            zero_padding = len(num_samples_str)
            for n in range(num_samples):
                # fill zero on n
                formatted_n = f"{n + 1:0{zero_padding}}"
                iter_expt_name = f"{expt_name}_[{num_samples}-{formatted_n}]"
                transformed_config[iter_expt_name] = iter_expt_config
        return transformed_config


class Status:
    """
    Managing the status and results of modules in Executor.
    """

    def __init__(self, config: Config):
        """
        Args:
            config (Config): The configuration object.

        Attributes:
            config (Config): The configuration object.
            sequence (list): The sequence of modules in the experiment.
            status (dict): A dictionary containing module Operators.
            metadata (dict[str, Metadata]):
                A dictionary containing the metadata of the dataset.
            exist_index (list):
                A list of unique already training indices generated by 'Splitter' modules.
            report (dict):
                A dictionary containing the report data generated by 'Reporter' modules.
        """
        self.config: Config = config
        self.sequence: list = config.sequence

        self.status: dict = {}
        self.metadata: dict[str, SchemaMetadata] = {}

        if "Splitter" in self.sequence:
            self.exist_index: list = []
        if "Reporter" in self.sequence:
            self.report: dict = {}

    def put(self, module: str, expt: str, operator: BaseOperator):
        """
        Add module status and operator to the status dictionary.
            Update exist_index when put Splitter.

        Args
            module (str):
                Current module name.
            expt (str):
                Current experiment name.
            operator (BaseOperator):
                Current Operator.
        """
        # renew status when 2nd,... rounds
        if module in self.status:
            module_seq_idx = self.sequence.index(module)
            module_to_keep = set(self.sequence[: module_seq_idx + 1])
            keys_to_remove = [key for key in self.status if key not in module_to_keep]
            for exist_module in keys_to_remove:
                del self.status[exist_module]

        if module in ["Loader", "Splitter", "Preprocessor"]:
            self.set_metadata(module, operator.get_metadata())

        if module == "Reporter":
            self.set_report(report=operator.get_result())

        temp = {}
        temp["expt"] = expt
        temp["operator"] = operator
        self.status[module] = temp

    def set_report(self, report: dict) -> None:
        """
        Add report data to the report dictionary.

        Args:
            report (dict): The report data.
        """
        if not hasattr(self, "report"):
            raise UnexecutedError

        # Report rows already combine in Reporter
        for eval_expt_name, report_data in report.items():
            self.report[eval_expt_name] = report_data.copy()

    def get_pre_module(self, curr_module: str) -> str:
        """
        Returns the previous module in the sequence based on the current module.

        Args:
            curr_module (str): The current module.

        Returns:
            (str) The previous module in the sequence if it exists,
                otherwise returns the latest module.
        """
        module_idx = self.sequence.index(curr_module)
        if module_idx == 0:
            return None
        else:
            return self.sequence[module_idx - 1]

    def get_result(self, module: str) -> Union[dict, pd.DataFrame]:
        """
        Retrieve the result of a specific module, optionally specifying a tag.
        """
        return self.status[module]["operator"].get_result()

    def get_full_expt(self, module: str = None) -> dict:
        """
        Retrieve a dictionary of module names and their corresponding experiment names.

        Args:
            module (str, optional): The module name. If provided,
                returns the experiment pairs up to and including the specified module.
                If not provided, returns all experiment pairs in the status.

        Returns:
            (dict) A dictionary containing the experiment pairs.
        """

        # Normal case: get all of expt pairs in status
        if module is None:
            return {
                seq_module: self.status[seq_module]["expt"]
                for seq_module in self.sequence
                if seq_module in self.status
            }

        # Special case: get expt pairs before given module (incl. module itself)
        else:
            if module not in self.sequence:
                raise ConfigError

            module_idx = self.sequence.index(module) + 1
            sub_sequence = self.sequence[:module_idx]
            return {
                seq_module: self.status[seq_module]["expt"]
                for seq_module in sub_sequence
            }

    def get_exist_index(self) -> list:
        """
        Retrieve the list of unique training indices generated by 'Splitter' modules.
        """
        return self.exist_index

    def set_metadata(self, module: str, metadata: SchemaMetadata) -> None:
        """
        Sets the metadata for a given module.

        Args:
            module (str): The name of the module.
            metadata (SchemaMetadata): The metadata to be set.
        """
        self.metadata[module] = metadata

    def get_metadata(self, module: str = "Loader") -> SchemaMetadata:
        """
        Retrieve the metadata of the dataset.

        Args:
            module (str, optional): The module name. Defaults to 'Loader'.
        """
        if module not in self.metadata:
            raise UnexecutedError
        return self.metadata[module]

    def get_synthesizer(self) -> Synthesizer:
        """
        Retrieve the synthesizer instance.
        """
        if "Synthesizer" in self.status:
            return self.status["Synthesizer"]["operator"].synthesizer
        else:
            raise UnexecutedError

    def get_processor(self) -> Processor:
        """
        Retrieve the processor of the dataset.
        """
        if "Preprocessor" in self.status:
            return self.status["Preprocessor"]["operator"].processor
        else:
            raise UnexecutedError

    def get_report(self) -> dict:
        """
        Retrieve the report data generated by 'Reporter' modules.
        """
        if not hasattr(self, "report"):
            raise UnexecutedError

        return self.report
