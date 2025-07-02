import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

import yaml

from petsard.config import Config
from petsard.config_base import BaseConfig
from petsard.exceptions import ConfigError
from petsard.status import Status


@dataclass
class ExecutorConfig(BaseConfig):
    """
    Defines the configuration for the Executor.

    Attr.:
        _logger (logging.Logger): The logger object.
        log_output_type (str): Output destination
            - stdout
            - file
            - both
        log_level (str): Logging level
            - DEBUG
            - INFO
            - WARNING
            - ERROR
            - CRITICAL
        log_dir (str): Directory for storing log files
        log_name (str): Log file name template (can include {timestamp})
    """

    log_output_type: str = "file"
    log_level: str = "INFO"
    log_dir: str = "."
    log_filename: str = "PETsARD_{timestamp}.log"

    def __post_init__(self):
        """
        Post-initialization method to validate the configuration.
        """
        super().__post_init__()
        if self.log_output_type not in ["stdout", "file", "both"]:
            raise ConfigError("Invalid log_output_type {self.log_output_type}")
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ConfigError("Invalid log_level {self.log_level}")


class Executor:
    """
    Represents an executor that runs a series of operators based on a given configuration.
    """

    def __init__(self, config: str):
        """
        Args:
            config (str): The configuration filename for the executor.

        Attributes:
            executor_config (ExecutorConfig): The configuration for the executor.
            _logger (logging.Logger): The logger object.
            config (Config): The configuration object.
            status (Status): The status of the executor.
            result (dict): The result of the executor.
        """

        # 1. set the default Executor
        self.executor_config = ExecutorConfig()

        # 2. set the default logger
        self._setup_logger()

        # 3. load the configuration
        self._logger.info(f"Loading configuration from {config}")
        yaml_config: dict = self._get_config(yaml_file=config)

        self.config = Config(config=yaml_config)
        self.sequence = self.config.sequence
        self.status = Status(config=self.config)
        self.result: dict = {}

    def _setup_logger(self, reconfigure=False):
        """
        Setting up the logger based on ExecutorConfig settings.

        Args:
            reconfigure (bool): If True, clear existing handlers before setup
        """
        if reconfigure:
            # If reconfigure, clear existing handlers
            root_logger = logging.getLogger("PETsARD")
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
        else:
            # If new configuration, disable the root logger
            logging.getLogger().handlers = []
            root_logger = logging.getLogger("PETsARD")

        # setup logging level
        root_logger.setLevel(getattr(logging, self.executor_config.log_level.upper()))

        # setup formatter
        formatter = logging.Formatter(
            "%(asctime)s - "  # timestamp
            "%(name)-21s - "  # logger name (left align w/ 21 digits: 'PETsARD.Postprocessor')
            "%(funcName)-17s - "  # function name (left align w/ 17 digits: 'inverse_transform')
            "%(levelname)-8s - "  # logger level (left align w/ 8 digits: 'CRITICAL')
            "%(message)s"  # message
        )

        # Handle file output
        if self.executor_config.log_output_type in ["file", "both"]:
            log_dir = self.executor_config.log_dir

            # Create log directory if it doesn't exist
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Create log file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_filename = self.executor_config.log_filename.replace(
                "{timestamp}", timestamp
            )
            log_path = os.path.join(log_dir, log_filename)

            # Create file handler
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Handle stdout output
        if self.executor_config.log_output_type in ["stdout", "both"]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # setup this logger as a child of root logger
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

    def _get_config(self, yaml_file: str) -> dict:
        """
        Load the configuration from a YAML file.
        """
        if not os.path.isfile(yaml_file):
            raise ConfigError(f"YAML file {yaml_file} does not exist")

        yaml_config: dict = {}
        with open(yaml_file) as yaml_file:
            yaml_config = yaml.safe_load(yaml_file)

        if "Executor" in yaml_config:
            self.executor_config.update(yaml_config["Executor"])

            self._setup_logger(reconfigure=True)
            self._logger.info("Logger reconfigured with settings from YAML")

            yaml_config.pop("Executor")

        return yaml_config

    def run(self):
        """
        run(): Runs the operators based on the configuration.
        """
        start_time: time = time.time()
        self._logger.info("Starting PETsARD execution workflow")
        while self.config.config.qsize() > 0:
            ops = self.config.config.get()
            module = self.config.module_flow.get()
            expt = self.config.expt_flow.get()

            self._logger.info(f"Executing {module} with {expt}")
            ops.run(ops.set_input(status=self.status))

            self.status.put(module, expt, ops)

            # collect result
            self._set_result(module)

        elapsed_time: time = time.time() - start_time
        formatted_elapsed_time: str = str(timedelta(seconds=round(elapsed_time)))
        self._logger.info(
            f"Completed PETsARD execution workflow (elapsed: {formatted_elapsed_time})"
        )

    def _set_result(self, module: str):
        """
        Get the result for a final module.

        Args:
            module (str): The name of the module.

        Returns:
            None. Update in self.result
        """
        if module == self.sequence[-1]:
            self._logger.debug(f"Collecting final results for {module}")
            full_expt = self.status.get_full_expt()
            full_expt_name = "_".join(
                [f"{module}[{expt}]" for module, expt in full_expt.items()]
            )
            self.result[full_expt_name] = self.status.get_result(module=module)

    def get_result(self):
        """
        Returns the result of the executor.
        """
        return self.result

    def get_timing(self):
        """
        取得執行時間記錄資料

        Returns:
            pd.DataFrame: 包含所有模組執行時間的 DataFrame
        """
        return self.status.get_timing_report_data()
