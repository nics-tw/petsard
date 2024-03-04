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


class PeekableQueue(queue.Queue):
    """
    A queue that allows peeking at the first element without removing it.
    """

    def peek(self):
        """Return the first element in the queue without removing it.

        Returns:
            The first element in the queue, or None if the queue is empty.
        """
        with self.mutex:
            return self.queue[0] if not self.empty() else None


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

    def __init__(self, filename: str):
        """
        Args:
            filename (str)
                The filename of config file.
        """
        self.config:      PeekableQueue = PeekableQueue()
        self.module_flow: PeekableQueue = PeekableQueue()
        self.expt_flow:   PeekableQueue = PeekableQueue()
        self.filename: str = filename
        self.sequence: list = []
        self.yaml: dict = {}

        with open(self.filename, 'r') as yaml_file:
            self.yaml = yaml.safe_load(yaml_file)

        self.sequence = list(self.yaml.keys())

        # Config check
        pattern = re.compile(r'_(\[[^\]]*\])$')
        for module, expt_config in self.yaml.items():
            for expt_name in expt_config:
                # any expt_name should not be postfix with "_[xxx]"
                if pattern.search(expt_name):
                    raise ConfigError
                # any expt_name should not contain "," for avoid report csv error
                if ',' in expt_name:
                    raise ConfigError

        if 'Splitter' in self.yaml:
            if 'method' not in self.yaml['Splitter']:
                self.yaml['Splitter'] = self._splitter_handler(
                    deepcopy(self.yaml['Splitter'])
                )

        self.config, self.module_flow, self.expt_flow = self._set_flow()

    def _set_flow(self) -> Tuple[PeekableQueue, PeekableQueue, PeekableQueue]:
        """
        Populate queues with module operators.

        Returns:
            flow (PeekableQueue):
                Peekable Queue containing the operators in the order they were traversed.
            module_flow (PeekableQueue):
                Peekable Queue containing the module names corresponding to each operator.
            expt_flow (PeekableQueue):
                Peekable Queue containing the experiment names corresponding to each operator.
        """
        flow:        PeekableQueue = PeekableQueue()
        module_flow: PeekableQueue = PeekableQueue()
        expt_flow:   PeekableQueue = PeekableQueue()

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
            num_samples = expt_config.get('num_samples', 1)
            iter_expt_config = deepcopy(expt_config)
            iter_expt_config['num_samples'] = 1

            num_samples_str = str(num_samples)
            zero_padding = len(num_samples_str)
            for n in range(num_samples):
                # fill zero on n
                formatted_n = f"{n+1:0{zero_padding}}"
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
            sequence (list): The sequence of modules in the experiment.
            status (dict): A dictionary containing module Operators.
            latest_module (str): Lastest module put in status.
            exist_index (list):
                A list of unique already training indices generated by 'Splitter' modules.
            report (dict):
                A dictionary containing the report data generated by 'Reporter' modules.
        """
        self.status: dict = {}
        self.config: Config = config
        self.sequence: list = config.sequence

        if 'Splitter' in self.sequence:
            self.exist_index: list = []
        if 'Reporter' in self.sequence:
            self.report: dict = {}

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
        # renew status when 2nd,... rounds
        if module in self.status:
            module_seq_idx = self.sequence.index(module)
            module_to_keep = set(self.sequence[:module_seq_idx + 1])
            keys_to_remove = [
                key for key in self.status if key not in module_to_keep
            ]
            for exist_module in keys_to_remove:
                del self.status[exist_module]

        if module == 'Reporter':
            result: dict = operator.get_result()
            if 'Reporter' in result:
                full_eval_expt_name: str = result['Reporter']['full_expt_name']
                report: pd.DataFrame = result['Reporter']['report']
                self.set_report(eval_name=full_eval_expt_name, report=report)

        temp = {}
        temp['expt'] = expt
        temp['operator'] = operator
        self.status[module] = deepcopy(temp)

    def set_report(self, eval_name: str, report: pd.DataFrame) -> None:
        """
        Add report data to the report dictionary.

        Args:
            eval_name (str): The evaluation name.
            report (pd.DataFrame): The report data.
        """
        if not hasattr(self, 'report'):
            raise UnexecutedError

        # Row combine should happens in Reporter, here directly replacement
        self.report[eval_name] = deepcopy(report)

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
                seq_module: self.status[seq_module]['expt']
                for seq_module in self.sequence if seq_module in self.status
            }

        # Special case: get expt pairs before given module (incl. module itself)
        else:
            if module not in self.sequence:
                raise ConfigError

            module_idx = self.sequence.index(module) + 1
            sub_sequence = self.sequence[:module_idx]
            return {
                seq_module: self.status[seq_module]['expt']
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

    def get_report(self) -> dict:
        """
        Retrieve the report data generated by 'Reporter' modules.
        """
        if not hasattr(self, 'report'):
            raise UnexecutedError

        return self.report
