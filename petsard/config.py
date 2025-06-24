import queue
import re
from copy import deepcopy
from typing import Tuple

from petsard.exceptions import ConfigError
from petsard.operator import (
    BaseOperator,  # noqa: F401 - Dynamic Imports
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
