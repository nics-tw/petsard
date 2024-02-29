from copy import deepcopy
import queue
import re
from typing import Tuple, Union

import pandas as pd
import yaml

from PETsARD.operator import (
    Operator,
    LoaderOperator,
    SplitterOperator,
    PreprocessorOperator,
    SynthesizerOperator,
    PostprocessorOperator,
    EvaluatorOperator,
    DescriberOperator,
    ReporterOperator
)
from PETsARD.processor import Processor
from PETsARD.error import ConfigError, UnexecutedError


class Sequence:
    """
    Initializes a sequence of modules for an experiment.
    """

    def __init__(self, sequence: list = None):
        """
        Args:
            sequence (list, optional):
                The user defined sequence of modules in the experiment.

        Attributes:
            default_sequence (list):
                The default sequence of modules.
            sequence (list):
                The sequence of modules for the experiment.
        """
        self.default_sequence: list = [
            'Loader', 'Splitter', 'Preprocessor', 'Synthesizer', 'Postprocessor', 'Evaluator'
        ]

        self.sequence: list = self.default_sequence if sequence is None else sequence


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

    def __init__(self, filename: str, sequence: list = None):
        """
        Args:
            filename (str)
                The filename of config file.
            sequence (list. Optional):
                The user defined sequence of modules in the experiment.
        """
        self.config:      queue.Queue = queue.Queue()
        self.module_flow: queue.Queue = queue.Queue()
        self.expt_flow:   queue.Queue = queue.Queue()
        self.filename = filename
        self.yaml: dict = {}

        self.sequence: list = Sequence(sequence).sequence

        with open(self.filename, 'r') as yaml_file:
            self.yaml = yaml.safe_load(yaml_file)

        # Config check: any expt_name should not be postfix with "_[xxx]"
        pattern = re.compile(r'_(\[[^\]]*\])$')
        for module, expt_config in self.yaml.items():
            for expt_name in expt_config:
                if pattern.search(expt_name):
                    raise ConfigError

        if 'Splitter' in self.yaml:
            if 'method' not in self.yaml['Splitter']:
                self.yaml['Splitter'] = self._splitter_handler(
                    deepcopy(self.yaml['Splitter'])
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
        flow:        queue.Queue = queue.Queue()
        module_flow: queue.Queue = queue.Queue()
        expt_flow:   queue.Queue = queue.Queue()

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
            config (dict):
                The original Splitter configuration.

        Returns:
            (dict):
                Transformed and expanded configuration dictionary.
        """
        transformed_config: dict = {}
        for expt_name, expt_config in config.items():
            num_samples = expt_config.get('num_samples', 1)
            iter_expt_config = deepcopy(expt_config)
            iter_expt_config['num_samples'] = 1

            num_samples_str = str(num_samples)
            zero_padding = len(num_samples_str)
            for n in range(num_samples):
                # fill zero on n
                formatted_n = f"{n+1:0{zero_padding}}"
                iter_expt_name = f"{expt_name}_[{formatted_n}|{num_samples}]"
                transformed_config[iter_expt_name] = iter_expt_config
        return transformed_config


class Status:
    """
    Managing the status and results of modules in Executor.

    Methods:
        put(module, expt, operator):
            Add module status and operator to the status dictionary.

        get_result(module, tag=None):
            Retrieve the result of a specific module, optionally specifying a tag.

        get_full_expt():
            Retrieve a dictionary of module names and their corresponding experiment names.

        get_exist_index():
            Retrieve the list of unique training indices generated by 'Splitter' modules.

    """

    def __init__(self, config: Config):
        """
        Args:
            config (Config): The configuration object.

        Attributes:
            sequence (list): The sequence of modules in the experiment.
            status (dict): A dictionary containing module Operators.
            latest_module (str): Lastest module put in status.
            exist_index (list):
                A list of unique already training indices generated by 'Splitter' modules.
        """
        self.status: dict = {}
        self.config: Config = config
        self.sequence: list = config.sequence
        self.latest_module: str = None

        if 'Splitter' in self.config.sequence:
            self.exist_index: list = []

    def put(self, module: str, expt: str, operator: Operator):
        """
        Add module status and operator to the status dictionary.
            Update exist_index when put Splitter.

        Args
            module (str):
                Current module name.
            expt (str):
                Current experiment name.
            operator (Operator):
                Current Operator.

        TODO self.exist_index
        """
        temp = {}
        temp['expt'] = expt
        temp['operator'] = operator
        self.status[module] = deepcopy(temp)

        self.latest_module = module

    def pre_module(self, curr_module: str) -> str:
        """
        Returns the previous module in the sequence based on the current module.

        Args:
            curr_module (str): The current module.

        Returns:
            (str) The previous module in the sequence if it exists,
                otherwise returns the latest module.
        """
        if curr_module == self.latest_module:
            module_idx = self.sequence.index(curr_module)
            if module_idx == 0:
                return None
            else:
                return self.sequence[module_idx - 1]
        else:
            return self.latest_module

    def get_result(self, module: str) -> Union[dict, pd.DataFrame]:
        """
        Retrieve the result of a specific module, optionally specifying a tag.
        """
        return self.status[module]['operator'].get_result()

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
                module: self.status[seq_module]['expt']
                for seq_module in self.sequence
            }

        # Special case: get expt pairs before given module (incl. module itself)
        else:
            if module not in self.sequence:
                raise ConfigError

            module_idx = self.sequence.index(module) + 1
            sub_sequence = self.sequence[:module_idx]
            return {
                module: self.status[seq_module]['expt']
                for seq_module in sub_sequence
            }

    def get_exist_index(self) -> list:
        """
        Retrieve the list of unique training indices generated by 'Splitter' modules.

        TODO confirm is exist_index is exist
        """
        return self.exist_index

    def get_metadata(self) -> dict:
        """
        Retrieve the metadata of the dataset.
        """
        if 'Loader' in self.status:
            return self.status['Loader']['operator'].loader.metadata
        else:
            raise UnexecutedError

    def get_processor(self) -> Processor:
        """
        Retrieve the processor of the dataset.
        """
        if 'Preprocessor' in self.status:
            return self.status['Preprocessor']['operator'].processor
        else:
            raise UnexecutedError
