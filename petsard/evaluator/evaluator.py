import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import pandas as pd

from petsard.config_base import BaseConfig
from petsard.evaluator.anonymeter import Anonymeter
from petsard.evaluator.customer_evaluator import CustomEvaluator
from petsard.evaluator.data_describer import DataDescriber
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.evaluator.mlutlity import MLUtility
from petsard.evaluator.mpuccs import MPUCCs
from petsard.evaluator.sdmetrics import SDMetricsSingleTable
from petsard.evaluator.stats import Stats
from petsard.exceptions import UncreatedError, UnsupportedMethodError


class EvaluatorMap(Enum):
    """
    Mapping of Evaluator.
    """

    DEFAULT: int = auto()
    # Protection
    ANONYMETER: int = auto()
    MPUCCS: int = auto()
    # Fidelity
    SDMETRICS: int = auto()
    STATS: int = auto()
    # Utility
    MLUTILITY: int = auto()
    # Describer
    DESCRIBE: int = auto()
    # Other
    CUSTOM_METHOD: int = auto()

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value before 1st dash (-)

        Args:
            method (str): evaluating method
        """
        # Get the string before 1st dash, if not exist, get emply ('').
        libname_match = re.match(r"^[^-]*", method)
        libname = libname_match.group() if libname_match else ""
        return cls.__dict__[libname.upper()]


@dataclass
class EvaluatorConfig(BaseConfig):
    """
    Configuration for the evaluator.

    Attributes:
        _logger (logging.Logger): The logger object.
        DEFAULT_EVALUATING_METHOD (str): The default method for evaluating the data.
        method (str): The method to be used for evaluating the data.
        method_code (int): The code of the evaluator method.
        eval_method (str): The name of the evaluator method.
            The difference between 'method' and 'eval_method' is that 'method' is the user input,
            while 'eval_method' is the actual method used for evaluating the data
        custom_params (dict): Any additional parameters to be stored in custom_params.
    """

    DEFAULT_EVALUATING_METHOD: str = "sdmetrics-single_table-qualityreport"

    method: str = "default"
    method_code: int = None
    eval_method: str = None

    custom_params: dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        class_name: str = self.__class__.__name__
        self._logger.debug(f"Initializing {class_name}")

        self._init_eval_method()

    def _init_eval_method(self) -> None:
        """
        Initialize the eval_method attribute based on the method_code.

        Designed to be overridden by subclasses to customize initialization logic.
        """
        try:
            self.method_code: int = EvaluatorMap.map(self.method.lower())
            self._logger.debug(
                f"Mapped evaluating method '{self.method}' to code {self.method_code}"
            )
        except KeyError:
            error_msg: str = f"Unsupported evaluator method: {self.method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Set the default
        self.eval_method: str = (
            self.DEFAULT_EVALUATING_METHOD
            if self.method_code == EvaluatorMap.DEFAULT
            else self.method
        )
        self._logger.info(
            f"EvaluatorConfig initialized with method: {self.method}, eval_method: {self.eval_method}"
        )


class Evaluator:
    """
    The Evaluator class is responsible for creating and evaluating a evaluator model,
    as well as analyzing data based on the evaluation criteria.
    """

    EVALUATOR_MAP: dict[int, BaseEvaluator] = {
        EvaluatorMap.DEFAULT: SDMetricsSingleTable,
        EvaluatorMap.ANONYMETER: Anonymeter,
        EvaluatorMap.MPUCCS: MPUCCs,
        EvaluatorMap.SDMETRICS: SDMetricsSingleTable,
        EvaluatorMap.STATS: Stats,
        EvaluatorMap.MLUTILITY: MLUtility,
        EvaluatorMap.DESCRIBE: DataDescriber,
        EvaluatorMap.CUSTOM_METHOD: CustomEvaluator,
    }

    def __init__(self, method: str, **kwargs):
        """
        Args:
            method (str): The method to be used for evaluating the data.
            **kwargs: Any additional parameters to be stored in custom_params.
            method (str): The method to be used for evaluating the data.
            **kwargs: Any additional parameters to be stored in custom_params.

        Attr:
            _logger (logging.Logger): The logger object.
            config (EvaluatorConfig): The configuration parameters for the evaluator.
            _impl (BaseEvaluator): The evaluator object.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info(
            f"Initializing {self.__class__.__name__} with method: {method}"
        )

        self._configure_implementation(method=method, **kwargs)

        self._impl: BaseEvaluator = None
        self._logger.info("≈ initialization completed")

    def _configure_implementation(self, method: str, **kwargs) -> None:
        """
        Configure the evaluator's implementation based on the specified method.
            This method handles the initialization
            of both configuration parameters and the implementation object
            according to the evaluation method provided.
            Designed to be overridden by subclasses to customize initialization logic.

        Args:
            method (str): The method to be used for evaluating the data.
            **kwargs: Any additional parameters to be stored in custom_params.
        """
        # Initialize the EvaluatorConfig object
        self.config: EvaluatorConfig = EvaluatorConfig(method=method)
        self._logger.debug("EvaluatorConfig successfully initialized")

        # Add custom parameters to the config
        if kwargs:
            self._logger.debug(
                f"Additional keyword arguments provided: {list(kwargs.keys())}"
            )
            self.config.update({"custom_params": kwargs})
            self._logger.debug("Config successfully updated with custom parameters")
        else:
            self._logger.debug("No additional parameters provided")

    def _create_evaluator_class(self) -> BaseEvaluator:
        """
        Create a Evaluator object with the configuration parameters.

        Designed to be overridden by subclasses to customize initialization logic.

        Returns:
            BaseEvaluator: The evaluator object.
        """
        return self.EVALUATOR_MAP[self.config.method_code]

    def create(self) -> None:
        """
        Create a Evaluator object with the given data.
        """
        self._logger.info("Creating {self.__class__.__name__} instance")

        evaluator_class = self._create_evaluator_class()
        self._logger.debug(
            f"Using {self.__class__.__name__} class: {evaluator_class.__name__}"
        )

        merged_config: dict = self.config.get_params(
            param_configs=[
                {"eval_method": {"action": "include"}},
                {"custom_params": {"action": "merge"}},
            ]
        )
        self._logger.debug(f"Merged config keys: {list(merged_config.keys())}")

        self._logger.info(f"Creating {evaluator_class.__name__} instance")
        self._impl = evaluator_class(
            config=merged_config,
        )
        self._logger.info(f"Successfully created {evaluator_class.__name__} instance")

    def eval(self, data: dict[str, pd.DataFrame]) -> None:
        """
        Evaluating the synthesizer model with the given data.


        Args:
            data (dict[str, pd.DataFrame])
                The dictionary contains necessary information.

                data = {
                    'ori': pd.DataFrame    # Original data used for synthesis
                    'syn': pd.DataFrame    # Synthetic data generated from 'ori'
                    'control: pd.DataFrame # Original data but NOT used for synthesis
                }

                Note:
                    1. Control is required in Anonymeter and MLUtility.
                    2. So it is recommended to split your original data before synthesizing it.
                        (We recommend to use our Splitter!)

        Returns:
            (dict[str, pd.DataFrame]): The evaluated report.
        """
        if self._impl is None:
            error_msg: str = "Synthesizer not created yet, call create() first"
            self._logger.warning(error_msg)
            raise UncreatedError(error_msg)

        time_start: time = time.time()

        self._logger.info(
            f"Evaluating data with keys {list(data.keys())} using evaluation method: {self.config.eval_method}"
        )
        evaluated_report: dict[str, pd.DataFrame] = self._impl.eval(data=data)
        time_spent: float = round(time.time() - time_start, 4)
        self._logger.info(f"Evaluation completed successfully in {time_spent} seconds")

        columns_info: list[str, list[str]] = {}
        dtype_counts: list[str, list[str]] = {}
        for key, df in data.items():
            columns_info[key] = list(df.columns)
            dtype_counts[key] = dict(df.dtypes.value_counts())

        self._logger.debug(
            f"Evaluation report summary: Data keys: {list(data.keys())}, "
            f"Column count by type per dataframe: {dtype_counts}, "
            f"Columns by key: {columns_info}"
        )

        return evaluated_report
