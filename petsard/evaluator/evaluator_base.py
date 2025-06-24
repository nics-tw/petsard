import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pandas as pd

from petsard.config_base import BaseConfig
from petsard.exceptions import ConfigError
from petsard.metadater.types.data_types import EvaluationScoreGranularityMap


@dataclass
class EvaluatorInputConfig(BaseConfig):
    """
    Configuration for the input data of evaluator.

    Attributes:
        _logger (logging.Logger): The logger object.
        data (pd.DataFrame, optional): The data used for evaluation.
        ori (pd.DataFrame, optional): The original data.
        syn (pd.DataFrame, optional): The synthetic data.
        control (pd.DataFrame, optional): The control data.
        major_key (str, optional): The major key of the data.
    """

    data: pd.DataFrame = None
    ori: pd.DataFrame = None
    syn: pd.DataFrame = None
    control: pd.DataFrame = None
    major_key: str = None

    def __post_init__(self):
        super().__post_init__()
        self._logger.debug("Initializing EvaluatorInputDataConfig")

    def verify_required_inputs(self, required_input_keys: str | list[str]) -> None:
        """
        Verify if the required inputs are provided.

        Args:
            required_input_keys (str | list[str]): The required input keys.

        Raises:
            ConfigError: If the required inputs are not provided.
        """
        error_msg: str = None

        # 1. Check input keys type
        if isinstance(required_input_keys, str):
            required_input_keys = [required_input_keys]

        if "Undefined" in required_input_keys:
            error_msg = "The required inputs are not defined."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # 2. Check if no major_key been given
        if self.major_key is None:
            if not set(required_input_keys).intersection({"ori", "data"}):
                error_msg = (
                    "There's mulitple keys in input, but no 'ori' or 'data' for aligning dtypes. "
                    f"Got keys: {required_input_keys}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
            self.major_key = "ori" if "ori" in required_input_keys else "data"

        # 3. Verify input keys
        missing: list[str] = []
        invalid: list[str] = []

        for key in required_input_keys:
            if key not in self.__dict__ or self.__dict__[key] is None:
                missing.append(key)
            elif not isinstance(self.__dict__[key], pd.DataFrame):
                invalid.append(key)

        if missing or invalid:
            error_parts = []
            if missing:
                error_parts.append(f"Missing required inputs: {missing}")
            if invalid:
                error_parts.append(f"Invalid inputs (not DataFrame): {invalid}")

            error_msg = ". ".join(error_parts)
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if len(required_input_keys) > 1:
            from petsard.metadater import Metadater

            reference_data: pd.DataFrame = getattr(self, self.major_key)
            reference_columns: set = set(reference_data.columns)

            # Create schema metadata using Metadater
            schema_metadata = Metadater.create_schema(
                dataframe=reference_data, schema_id="reference_schema"
            )

            other_keys: list[str] = [
                key for key in required_input_keys if key != self.major_key
            ]

            # 4. Check column difference
            column_mismatches: dict[str, list[str]] = {}
            other_key_columns: list[str] = []
            for other_key in other_keys:
                other_key_columns = set(getattr(self, other_key).columns)

                # Find differences
                missing_cols = reference_columns - other_key_columns
                extra_cols = other_key_columns - reference_columns

                if missing_cols or extra_cols:
                    column_mismatches[other_key] = {
                        "missing": list(missing_cols),
                        "extra": list(extra_cols),
                    }

            if column_mismatches:
                error_msg = (
                    f"Column name mismatch between dataframes: {column_mismatches}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # 5. align dtypes using schema functions
            for other_key in other_keys:
                other_data = getattr(self, other_key)
                # Apply schema transformations to align dtypes
                from petsard.metadater.schema.schema_functions import (
                    apply_schema_transformations,
                )

                aligned_data = apply_schema_transformations(
                    data=other_data,
                    schema=schema_metadata,
                )
                setattr(self, other_key, aligned_data)


@dataclass
class EvaluatorScoreConfig(BaseConfig):
    """
    Configuration for the scoring result of evaluator.

    Attributes:
        _logger (logging.Logger): The logger object.
    """

    available_scores_granularity: list[str]

    def __post_init__(self):
        super().__post_init__()

        # Check the granularity validity
        for granularity in self.available_scores_granularity:
            try:
                _ = EvaluationScoreGranularityMap.map(granularity)
            except KeyError:
                error_msg: str = f"Non-default granularity '{granularity}' is used."
                self._logger.info(error_msg)

    def _verify_scores_granularity(self, scores: dict[str, Any]) -> None:
        """
        Verify the granularity of the scores.

        Args:
            scores (dict[str, Any]): The scores to be verified.

        Raises:
            ConfigError: If the granularity is not valid.
        """
        error_msg: str = None

        if not isinstance(scores, dict):
            error_msg = "Scores should be a dictionary."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # find out key in scores but not in available_scores_granularity
        unexpected_keys: set = set(scores.keys()) - set(
            self.available_scores_granularity
        )
        # find out key in available_scores_granularity but not in scores
        missing_keys = set(self.available_scores_granularity) - set(scores.keys())

        if unexpected_keys or missing_keys:
            if unexpected_keys:
                error_msg += f"Unexpected granularity levels in scores: {', '.join(unexpected_keys)}. "
            if missing_keys:
                error_msg += (
                    f"Missing granularity levels in scores: {', '.join(missing_keys)}."
                )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)


class BaseEvaluator(ABC):
    """
    Base class for all evaluator/describer engine implementations.
    These engines are used by the main Evaluator/Describer to perform the actual data evaluating.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["Undefined"]

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.
                - eval_method (str): The method of how you evaluating data.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): A dictionary containing the configuration settings.
            _impl (Any): The evaluator object.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        if not isinstance(config, dict):
            error_msg: str = "The config parameter must be a dictionary."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if "eval_method" not in config:
            error_msg: str = (
                "The 'eval_method' parameter is required for the synthesizer."
            )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        self.config: dict = config
        self._impl: Any = None

    @abstractmethod
    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the evaluator.
            _impl should be initialized in this method.

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
        error_msg: str = "The '_eval' method must be implemented in the derived class."
        self._logger.error(error_msg)
        raise NotImplementedError(error_msg)

    def eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Create the Describer/Evaluator.

        Args:
            data (dict): same as _eval() method.

        Returns:
            (dict[str, pd.DataFrame]): same as _eval() method.
        """
        data_params: EvaluatorInputConfig = EvaluatorInputConfig.from_dict(data)

        # Verify the required inputs
        data_params.verify_required_inputs(self.REQUIRED_INPUT_KEYS)

        merged_config: dict = data_params.get_params(
            param_configs=[
                {attr: {"action": "INCLUDE"}} for attr in self.REQUIRED_INPUT_KEYS
            ]
        )
        self._logger.debug(f"Merged config keys: {list(merged_config.keys())}")

        # Evaluate the data
        self._logger.info(f"Evaluating {self.__class__.__name__}")
        evaluated_report: dict[str, pd.DataFrame] = self._eval(merged_config)
        self._logger.info(f"Successfully evaluating {self.__class__.__name__}")

        return evaluated_report
