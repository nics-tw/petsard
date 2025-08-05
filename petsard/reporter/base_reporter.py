"""
純函式化的 BaseReporter
完全無狀態設計，專注於抽象介面定義
"""

import re
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any, Final

import pandas as pd

from petsard.exceptions import ConfigError, UnsupportedMethodError


class ReporterMethod(IntEnum):
    """Enumeration for reporter methods."""

    SAVE_DATA = 1
    SAVE_REPORT = 2
    SAVE_TIMING = 3

    @classmethod
    def map(cls, method: str) -> "ReporterMethod":
        """
        Get method mapping enum value from string.

        Args:
            method (str): reporting method (case-insensitive)

        Returns:
            ReporterMethod: Corresponding enum value

        Raises:
            UnsupportedMethodError: If method name is not supported
        """
        method_mapping = {
            "SAVE_DATA": cls.SAVE_DATA,
            "SAVE_REPORT": cls.SAVE_REPORT,
            "SAVE_TIMING": cls.SAVE_TIMING,
        }

        try:
            return method_mapping[method.upper()]
        except KeyError as err:
            raise UnsupportedMethodError from err


class ReportGranularity(IntEnum):
    """Enumeration for report granularity types."""

    GLOBAL = 1
    COLUMNWISE = 2
    PAIRWISE = 3
    DETAILS = 4
    TREE = 5

    @classmethod
    def map(cls, granularity: str) -> "ReportGranularity":
        """
        Get granularity mapping enum value from string.

        Args:
            granularity (str): reporting granularity (case-insensitive)

        Returns:
            ReportGranularity: Corresponding enum value

        Raises:
            UnsupportedMethodError: If granularity is not supported
        """
        granularity_mapping = {
            "GLOBAL": cls.GLOBAL,
            "COLUMNWISE": cls.COLUMNWISE,
            "PAIRWISE": cls.PAIRWISE,
            "DETAILS": cls.DETAILS,
            "TREE": cls.TREE,
        }

        try:
            return granularity_mapping[granularity.upper()]
        except KeyError as err:
            raise UnsupportedMethodError from err


class ModuleNames:
    """Constants for module names used in PETsARD pipeline."""

    # Core pipeline modules
    LOADER: Final[str] = "Loader"
    SPLITTER: Final[str] = "Splitter"
    PROCESSOR: Final[str] = "Processor"
    PREPROCESSOR: Final[str] = "Preprocessor"
    SYNTHESIZER: Final[str] = "Synthesizer"
    POSTPROCESSOR: Final[str] = "Postprocessor"
    CONSTRAINER: Final[str] = "Constrainer"
    EVALUATOR: Final[str] = "Evaluator"
    DESCRIBER: Final[str] = "Describer"
    REPORTER: Final[str] = "Reporter"

    # Module lists
    ALL_MODULES: Final[list[str]] = [
        LOADER,
        SPLITTER,
        PROCESSOR,
        PREPROCESSOR,
        SYNTHESIZER,
        POSTPROCESSOR,
        CONSTRAINER,
        EVALUATOR,
        DESCRIBER,
        REPORTER,
    ]

    REPORT_AVAILABLE_MODULES: Final[list[str]] = [
        EVALUATOR,
        DESCRIBER,
    ]


class DataFrameConstants:
    """Constants for DataFrame operations."""

    # Column names for merging operations
    REPLACE_TAG: Final[str] = "_petsard|_replace"
    RIGHT_SUFFIX: Final[str] = "|_petsard|_right"

    # Standard column names
    FULL_EXPT_NAME: Final[str] = "full_expt_name"
    COLUMN: Final[str] = "column"
    COLUMN1: Final[str] = "column1"
    COLUMN2: Final[str] = "column2"

    # Merge-related columns
    MERGE_COLUMNS: Final[list[str]] = [
        FULL_EXPT_NAME,
        COLUMN,
        COLUMN1,
        COLUMN2,
    ]


class RegexPatterns:
    """Pre-compiled regular expression patterns."""

    # Experiment name pattern: "eval_name_[granularity]"
    EVAL_EXPT_NAME: Final[re.Pattern] = re.compile(r"^([A-Za-z0-9_-]+)_\[([\w-]+)\]$")

    # Pattern for removing postfix "_[xxx]" from experiment names
    POSTFIX_REMOVAL: Final[re.Pattern] = re.compile(r"_(\[[^\]]*\])$")


class ConfigDefaults:
    """Default configuration values."""

    DEFAULT_OUTPUT_PREFIX: Final[str] = "petsard"


def convert_full_expt_tuple_to_name(expt_tuple: tuple) -> str:
    """
    Convert a full experiment tuple to a name.

    Args:
        expt_tuple (tuple): A tuple representing a full experiment configuation.
            Each pair within the tuple should consist of a module name
            followed by its corresponding experiment name.
            The tuple can contain multiple such pairs,
            indicating a sequence of module and experiment steps. e.g.
            - A single step experiment: ('Loader', 'default'),
            - A multi-step experiment: ('Loader', 'default', 'Preprocessor', 'default')

    Returns:
        (str): A string representation of the experiment configuration,
            formatted as
            `ModuleName[ExperimentName]` for single-step experiments or
            `ModuleName[ExperimentName]_AnotherModuleName[AnotherExperimentName]`
            for multi-step experiments.
            - A single step experiment: 'Loader[default]'
            - A multi-step experiment: 'Loader[default]_Preprocessor[default]'
    """
    return "_".join(
        [f"{expt_tuple[i]}[{expt_tuple[i + 1]}]" for i in range(0, len(expt_tuple), 2)]
    )


class BaseReporter(ABC):
    """
    純函式化的基礎 Reporter 類

    完全無狀態設計，專注於抽象介面定義
    所有實作都應該是純函式，不維護任何實例狀態
    """

    ALLOWED_IDX_MODULE: list = ModuleNames.ALL_MODULES
    SAVE_REPORT_AVAILABLE_MODULE: list = ModuleNames.REPORT_AVAILABLE_MODULES

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration settings for the report.
                - method (str): The method used for reporting.
                - output (str, optional):
                    The output filename prefix for the report.
                    Default is 'petsard'.
        """
        self.config: dict = config

        if "method" not in self.config:
            raise ConfigError
        if not isinstance(self.config.get("output"), str) or not self.config["output"]:
            self.config["output"] = ConfigDefaults.DEFAULT_OUTPUT_PREFIX

    @abstractmethod
    def create(self, data: dict) -> Any:
        """
        純函式：處理資料並返回結果

        Args:
            data (dict): The data used for creating the report.
                See BaseReporter._verify_create_input() for format requirement.

        Returns:
            Any: 處理後的資料
        """
        raise NotImplementedError

    @abstractmethod
    def report(self, processed_data: Any = None) -> Any:
        """
        純函式：生成並保存報告

        Args:
            processed_data (Any): 處理後的資料

        Returns:
            Any: 生成的報告資料
        """
        raise NotImplementedError

    @classmethod
    def _verify_create_input(cls, data: dict) -> None:
        """
        Verify the input data for the create method.

        Validates the structure and type of input data intended for creating a report.
        Invalid entries will be removed and logged.

        Args:
            data (dict): Input data for report creation.

        Raises:
            ConfigError: If any validation check fails.
        """
        import logging

        logger = logging.getLogger(f"PETsARD.{__name__}")
        keys_to_remove = []

        for idx, value in data.items():
            if idx == "exist_report":
                # Handle exist_report validation
                if cls._validate_exist_report(idx, value, keys_to_remove, logger):
                    continue
            else:
                # Handle regular data entry validation
                cls._validate_data_entry(idx, value, keys_to_remove, logger)

        # Remove invalid keys and log summary
        cls._cleanup_invalid_entries(data, keys_to_remove, logger)

    @classmethod
    def _validate_exist_report(
        cls, idx: str, value, keys_to_remove: list, logger
    ) -> bool:
        """
        Validate exist_report entry.

        Args:
            idx (str): The index key.
            value: The value to validate.
            keys_to_remove (list): List to collect invalid keys.
            logger: Logger instance.

        Returns:
            bool: True if validation handled, False otherwise.
        """
        if not isinstance(value, dict):
            logger.info(
                f"Removing 'exist_report': Expected dict, got {type(value).__name__}"
            )
            keys_to_remove.append(idx)
            return True

        # Clean exist_report entries
        exist_report_keys_to_remove = []
        for exist_key, exist_value in value.items():
            if exist_value is not None and not isinstance(exist_value, pd.DataFrame):
                logger.info(
                    f"Removing exist_report['{exist_key}']: "
                    f"Expected pd.DataFrame or None, got {type(exist_value).__name__}"
                )
                exist_report_keys_to_remove.append(exist_key)

        # Remove invalid entries from exist_report
        for key in exist_report_keys_to_remove:
            del value[key]

        # If exist_report is now empty, remove it entirely
        if not value:
            logger.info("Removing 'exist_report': All entries were invalid")
            keys_to_remove.append(idx)

        return True

    @classmethod
    def _validate_data_entry(cls, idx, value, keys_to_remove: list, logger) -> None:
        """
        Validate regular data entry.

        Args:
            idx: The index tuple.
            value: The value to validate.
            keys_to_remove (list): List to collect invalid keys.
            logger: Logger instance.
        """
        # Check if index has even number of elements
        if not cls._validate_index_structure(idx, keys_to_remove, logger):
            return

        # Check module names validity
        if not cls._validate_module_names(idx, keys_to_remove, logger):
            return

        # Check value type
        cls._validate_value_type(idx, value, keys_to_remove, logger)

    @classmethod
    def _validate_index_structure(cls, idx, keys_to_remove: list, logger) -> bool:
        """
        Validate that index has even number of elements.

        Args:
            idx: The index tuple.
            keys_to_remove (list): List to collect invalid keys.
            logger: Logger instance.

        Returns:
            bool: True if valid, False otherwise.
        """
        if len(idx) % 2 != 0:
            logger.info(f"Removing key {idx}: Index must have even number of elements")
            keys_to_remove.append(idx)
            return False
        return True

    @classmethod
    def _validate_module_names(cls, idx, keys_to_remove: list, logger) -> bool:
        """
        Validate module names in the index.

        Args:
            idx: The index tuple.
            keys_to_remove (list): List to collect invalid keys.
            logger: Logger instance.

        Returns:
            bool: True if valid, False otherwise.
        """
        module_names = idx[::2]

        # Check if all module names are allowed
        if not all(module in cls.ALLOWED_IDX_MODULE for module in module_names):
            invalid_modules = [
                m for m in module_names if m not in cls.ALLOWED_IDX_MODULE
            ]
            logger.info(f"Removing key {idx}: Invalid module names: {invalid_modules}")
            keys_to_remove.append(idx)
            return False

        # Check for duplicate module names
        if len(module_names) != len(set(module_names)):
            logger.info(f"Removing key {idx}: Duplicate module names found")
            keys_to_remove.append(idx)
            return False

        return True

    @classmethod
    def _validate_value_type(cls, idx, value, keys_to_remove: list, logger) -> None:
        """
        Validate that value is pd.DataFrame or None.

        Args:
            idx: The index tuple.
            value: The value to validate.
            keys_to_remove (list): List to collect invalid keys.
            logger: Logger instance.
        """
        if value is not None and not isinstance(value, pd.DataFrame):
            logger.info(
                f"Removing key {idx}: "
                f"Expected pd.DataFrame or None, got {type(value).__name__}"
            )
            keys_to_remove.append(idx)

    @classmethod
    def _cleanup_invalid_entries(cls, data: dict, keys_to_remove: list, logger) -> None:
        """
        Remove invalid keys and log summary.

        Args:
            data (dict): The data dictionary to clean up.
            keys_to_remove (list): List of keys to remove.
            logger: Logger instance.
        """
        # Remove invalid keys
        for key in keys_to_remove:
            del data[key]

        # Log summary if any keys were removed
        if keys_to_remove:
            logger.info(
                f"Removed {len(keys_to_remove)} invalid entries from input data"
            )

    def _save(self, data: pd.DataFrame, full_output: str) -> None:
        """
        Save the data to a CSV file.

        Args:
            data (pd.DataFrame): The data to be saved.
            full_output (str): The full output path for the CSV file.
        """
        import logging

        logger = logging.getLogger(f"PETsARD.{__name__}")
        logger.info(f"Saving report to {full_output}.csv")
        data.to_csv(path_or_buf=f"{full_output}.csv", index=False, encoding="utf-8")
