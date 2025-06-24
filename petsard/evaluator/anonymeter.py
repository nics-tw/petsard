import logging
import re
import warnings
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import pandas as pd
from anonymeter.evaluators import (
    InferenceEvaluator,
    LinkabilityEvaluator,
    SinglingOutEvaluator,
)

from petsard.config_base import BaseConfig
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.metadater.types.data_types import safe_round


class AnonymeterMap(Enum):
    """
    map of Anonymeter
    """

    SINGLINGOUT: int = auto()
    LINKABILITY: int = auto()
    INFERENCE: int = auto()

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        return cls.__dict__[re.sub(r"^anonymeter-", "", method).upper()]


@dataclass
class AnonymeterConfig(BaseConfig):
    """
    Configuration for the Anonymeter Evaluator.

    Attributes:
        _logger (logging.Logger): The logger object.
        eval_method (str): The method of how you evaluating data.
        eval_method_code (int, optional): The code of the evaluator method.
        AVAILABLE_MODES (list[str]): The available modes for SinglingOut.
        n_attacks (int, optional):
            The number of attack attempts using the specified attack method.
        max_n_attacks (bool, optional):
            Determines whether to enforce the maximum number of attacks.
            Support only for Linkability and Inference.
        max_attempts (int, optional):
            The maximum number of singling-out attempts to find a valid query.
        n_cols (int, optional):
            The number of columns used for generating singling-out queries.
        mode (str, optional): The mode of singling-out evaluation.
        n_neighbors (int, optional):
            Sets the number of nearest neighbors to consider for each entry in the search.
            Indicating a successful linkability attack only if
            the closest synthetic record matches for both split original records.
        aux_cols (tuple[list[str], list[str]], optional):
            Features of the records that are given to the attacker as auxiliary information.
            The Anonymeter documentation states it supports 'tuple of int',
            but this is not reflected in their type annotations,
            so we will omit it here and only mention this for reference.
        secret (str | list[str], optional):
            The secret attribute(s) of the target records, unknown to the attacker.
            This is what the attacker will try to guess.
        n_jobs (int, optional):
            Specifies the number of jobs Anonymeter will use. Not supported for SinglingOut.
            -1 means all threads except one. -2 means every thread.
        ori (pd.DataFrame): The original data.
        syn (pd.DataFrame): The synthetic data.
        control (pd.DataFrame): The control data.
    """

    eval_method: str
    eval_method_code: int = None

    AVAILABLE_MODES: list[str] = field(
        default_factory=lambda: ["multivariate", "univariate"]
    )

    n_attacks: int = 2000
    max_n_attacks: bool = False
    max_attempts: int = 500000
    n_cols: int = 3
    mode: str = "multivariate"
    n_neighbors: int = 1
    aux_cols: tuple[list[str], list[str]] = None
    secret: str | list[str] = None
    n_jobs: int = -2
    ori: pd.DataFrame = None
    syn: pd.DataFrame = None
    control: pd.DataFrame = None

    def __post_init__(self):
        super().__post_init__()
        error_msg: str = None

        try:
            self.eval_method_code = AnonymeterMap.map(self.eval_method)
        except KeyError:
            error_msg = f"Unsupported evaluator method: {self.eval_method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if self.n_attacks <= 0:
            error_msg = "The number of attacks must be greater than 0."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if self.n_jobs == 0 or self.n_jobs < -2:
            error_msg = "The number of jobs must be -2, -1, or greater than 0."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if self.eval_method_code == AnonymeterMap.SINGLINGOUT:
            if self.mode not in self.AVAILABLE_MODES:
                error_msg = f"Unsupported mode for SinglingOut: {self.mode}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
            elif self.mode == "univariate":
                self._logger.info(
                    f"n_cols setting {self.n_cols} will be ignored "
                    "due to SinglingOut mode set to 'univariate'"
                )
                self.n_cols = None
            else:  # multivariate
                if self.n_cols <= 0:
                    error_msg = "The number of singling-out attack columns must be greater than 0."
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

            if self.max_attempts <= 0:
                error_msg = "The maximum number of attempts must be greater than 0."
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            self.n_neighbors = None
            self.aux_cols = None
            self.secret = None
            self.n_jobs = None
        elif self.eval_method_code in [
            AnonymeterMap.LINKABILITY,
            AnonymeterMap.INFERENCE,
        ]:
            self.max_attempts = None
            self.n_cols = None
            self.mode = None

            if self.max_n_attacks:
                self._logger.info(
                    "max_n_attacks is set, the maximum number, 'n_attacks' will be adjusted"
                )

            if self.eval_method_code == AnonymeterMap.LINKABILITY:
                if self.aux_cols is None:
                    error_msg = (
                        "The auxiliary columns must be provided for Linkability."
                    )
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)
                elif (
                    len(self.aux_cols) != 2
                    or not (
                        isinstance(self.aux_cols[0], list)
                        and isinstance(self.aux_cols[1], list)
                    )
                    or not all(
                        isinstance(item, str)
                        for item in self.aux_cols[0] + self.aux_cols[1]
                    )
                ):
                    error_msg = (
                        "The auxiliary columns must be a tuple of two lists of strings."
                    )
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)
                elif set(self.aux_cols[0]).intersection(set(self.aux_cols[1])):
                    overlapping_columns: set[str] = set(self.aux_cols[0]).intersection(
                        set(self.aux_cols[1])
                    )
                    error_msg = (
                        f"The two lists in auxiliary columns must not have overlapping elements. "
                        f"Found overlapping elements: {overlapping_columns}"
                    )
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)
            else:  # Inference
                if self.aux_cols is not None:
                    if not isinstance(self.aux_cols, list) or not all(
                        isinstance(item, str) for item in self.aux_cols
                    ):
                        error_msg = "The auxiliary columns must be a list of strings."
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)

                    if self.secret is None:
                        error_msg = (
                            "The secret attribute(s) must be provided for Inference."
                        )
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
                    else:
                        if self.secret in self.aux_cols:
                            error_msg = "The secret attribute(s) must not be included in the auxiliary columns."
                            self._logger.error(error_msg)
                            raise ConfigError(error_msg)

    def update_data(self, data: dict) -> None:
        error_msg: str = None

        self.ori = data["ori"]
        self.syn = data["syn"]
        self.control = data["control"]

        if self.eval_method_code == AnonymeterMap.SINGLINGOUT:
            if self.n_cols > self.ori.shape[1]:
                error_msg = (
                    "The singling must be less than the number of columns in the data."
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

        elif self.eval_method_code in [
            AnonymeterMap.LINKABILITY,
            AnonymeterMap.INFERENCE,
        ]:
            if self.max_n_attacks:
                ori_n_attacks: int = self.n_attacks
                self.max_n_attacks = self.control[0]
                self._logger.info(
                    f"Adjusted 'n_attacks' from {ori_n_attacks} to {self.n_attacks} "
                    "due to 'max_n_attacks'"
                )

            if self.eval_method_code == AnonymeterMap.INFERENCE:
                if self.aux_cols is None:
                    self.aux_cols = [
                        col for col in self.ori.columns if col != self.secret
                    ]

            all_aux_cols: list[str] = (
                self.aux_cols[0] + self.aux_cols[1]
                if self.eval_method_code == AnonymeterMap.LINKABILITY
                else self.aux_cols
            )
            invalid_columns: list[str] = [
                col for col in all_aux_cols if col not in self.ori.columns
            ]
            if invalid_columns:
                error_msg = f"The following auxiliary columns do not exist in the original data: {invalid_columns}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            if self.eval_method_code == AnonymeterMap.INFERENCE:
                if self.secret not in self.ori.columns:
                    error_msg = f"The secret attribute(s) '{self.secret}' must exist in the original data."
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)


class Anonymeter(BaseEvaluator):
    """
    Factory for Anonymeter Evaluator.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn", "control"]
    ANONYMETER_CLASS_MAP: dict[int, Any] = {
        AnonymeterMap.SINGLINGOUT: SinglingOutEvaluator,
        AnonymeterMap.LINKABILITY: LinkabilityEvaluator,
        AnonymeterMap.INFERENCE: InferenceEvaluator,
    }
    REQUIRED_ANONYMETER_KEYS: list[str] = [
        "ori",
        "syn",
        "control",
        "n_attacks",
    ]
    REQUIRED_ANONYMETER_KEYS_MAP: dict[int, list[str]] = {
        AnonymeterMap.SINGLINGOUT: (
            REQUIRED_ANONYMETER_KEYS + ["n_cols", "max_attempts"]
        ),
        AnonymeterMap.LINKABILITY: (
            REQUIRED_ANONYMETER_KEYS + ["n_neighbors", "aux_cols"]
        ),
        AnonymeterMap.INFERENCE: (REQUIRED_ANONYMETER_KEYS + ["secret", "aux_cols"]),
    }
    MAX_ATTEMPTS_OF_RUNTIME_ERROR: int = 10
    REQUIRED_ANONYMETER_KEYS_EVALUATE_MAP: dict[int, list[str]] = {
        AnonymeterMap.SINGLINGOUT: ["mode"],
        AnonymeterMap.LINKABILITY: ["n_jobs"],
        AnonymeterMap.INFERENCE: ["n_jobs"],
    }
    AVAILABLE_SCORES_GRANULARITY: list[str] = [
        "global",
        "details",
    ]

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.
                - eval_method (str): The method of how you evaluating data.

        Attr:
            REQUIRED_INPUT_KEYS (list[str]): The required keys for the input data.
            ANONYMETER_CLASS_MAP (dict[int, Any]): The mapping of the Anonymeter classes.
            REQUIRED_ANONYMETER_KEYS (list[str]): The required keys for the Anonymeter.
            REQUIRED_ANONYMETER_KEYS_MAP (dict[int, list[str]]):
            MAX_ATTEMPTS_OF_RUNTIME_ERROR (int): The maximum number of attempts for runtime error.
            REQUIRED_ANONYMETER_KEYS_EVALUATE_MAP (dict[int, list[str]]):
            AVAILABLE_SCORES_GRANULARITY (list[str]): The available scores granularity.
            _logger (logging.Logger): The logger object.
            config (dict): A dictionary containing the configuration settings.
            anonymeter_config (AnonymeterConfig):
                The configuration parameters for the anonymeter.
            _impl (Any): The evaluator object.
        """
        super().__init__(config=config)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        self._logger.debug(f"Verify AnonymeterConfig with parameters: {self.config}")
        self.anonymeter_config = AnonymeterConfig(**self.config)
        self._logger.debug(
            "AnonymeterConfig successfully initialized as {self.anonymeter_config}"
        )

        self._impl: Any = None

    def _extract_scores(self) -> dict[str, Any]:
        """
        _extract_scores of Anonymeter.
            Uses .risk()/.results() method in Anonymeter
            to extract result from self._impl into the designated dictionary.

        Return
            (dict[str, Any]). Result as specific format describe in eval().
        """

        result: dict[str, Any] = {}

        # Handle the risk
        try:
            risk = self._impl.risk()
            result["risk"] = safe_round(risk.value)
            result["risk_CI_btm"] = safe_round(risk.ci[0])
            result["risk_CI_top"] = safe_round(risk.ci[1])
        except Exception:
            result["risk"] = pd.NA
            result["risk_CI_btm"] = pd.NA
            result["risk_CI_top"] = pd.NA

        # Handle the attack_rate, baseline_rate, control_rate
        try:
            results = self._impl.results()
            for rate_type in ["attack_rate", "baseline_rate", "control_rate"]:
                rate_result = getattr(results, rate_type, None)
                if rate_result:
                    result[f"{rate_type}"] = safe_round(rate_result.value)
                    result[f"{rate_type}_err"] = safe_round(rate_result.error)
                else:
                    result[f"{rate_type}"] = pd.NA
                    result[f"{rate_type}_err"] = pd.NA
        except Exception:
            for rate_type in ["attack_rate", "baseline_rate", "control_rate"]:
                result[f"{rate_type}"] = pd.NA
                result[f"{rate_type}_err"] = pd.NA
            error_msg: str = "There's no result for attack_rate, recorded as NA."
            self._logger.warning(error_msg)

        return result

    def _get_global(self, anonymeter_scores: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Retrieves the global result from the Anonymeter.

        Args:
            anonymeter_scores (dict[str, pd.DataFrame]): The scores of the Anonymeter.

        Returns:
            (pd.DataFrame): A DataFrame with the global evaluation result.
                One row only for representing the whole data result.
        """

        return pd.DataFrame.from_dict(
            data={"result": anonymeter_scores}, orient="columns"
        ).T

    def _get_details(
        self, anonymeter_scores: dict[str, pd.DataFrame]
    ) -> dict[str, Any]:
        """
        Retrieves the specify details of the evaluation.

        Args:
            anonymeter_scores (dict[str, pd.DataFrame]): The scores of the Anonymeter.

        Returns:
            (dict[str, Any]): The details of the evaluation.
        """
        if self.anonymeter_config.eval_method_code == AnonymeterMap.INFERENCE:
            return None  # Inference queries didn't been stored

        details: dict[str, Any] = {}

        # SinglingOut attacks of Univariate. control queries didn't been stored
        if self.anonymeter_config.eval_method_code == AnonymeterMap.SINGLINGOUT:
            details["attack_queries"] = self._impl.queries(baseline=False)
            details["baseline_queries"] = self._impl.queries(baseline=True)
        # Linkability: Dict[int, Set(int)], aux_cols[0] indexes links to aux_cols[1]
        elif self.anonymeter_config.eval_method_code == AnonymeterMap.LINKABILITY:
            n_neighbors = self.anonymeter_config.n_neighbors
            details["attack_links"] = self._impl._attack_links.find_links(
                n_neighbors=n_neighbors
            )
            details["baseline_links"] = self._impl._baseline_links.find_links(
                n_neighbors=n_neighbors
            )
            details["control_links"] = self._impl._control_links.find_links(
                n_neighbors=n_neighbors
            )

        return details

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the evaluator.
            _impl should be initialized in this method.

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.

        Returns:
            (dict) Result as following key-value pairs:
            - risk (float)
                Privacy Risk value of specified attacks. Ranging from 0 to 1.
                    A value of 0 indicates no risk, and 1 indicates full risk.
                Includes risk_ci_btm and risk_ci_top
                    for the bottom and top of the confidence interval.
            - attack_Rate (float)
                Main attack rate of specified attacks, which the attacker
                    uses the synthetic datase to deduce private information of records
                    in the original/training dataset. Ranging from 0 to 1.
                A value of 0 indicates none of success attack,
                    and 1 indicates totally success attack.
                Includes attack_Rate_err for its error rate.
            - baseline_Rate (float)
                Naive, or Baseline attack rate of specified attacks, which is
                    carried out based on random guessing, to provide a baseline against
                    which the strength of the “main” attack can be compared.
                    Ranging from 0 to 1.
                A value of 0 indicates none of success attack,
                    and 1 indicates totally success attack.
                Includes baseline_Rate_err for its error rate.
            - control_Rate (float)
                Control attack rate of specified attacks,  hich is conducted on
                    a set of control dataset, to distinguish the concrete privacy risks
                    of the original data records (i.e., specific information)
                    from general risks intrinsic to the whole population (i.e., generic information).
                    Ranging from 0 to 1.
                A value of 0 indicates none of success attack,
                    and 1 indicates totally success attack.
                Includes control_Rate_err for its error rate.
        """

        self.anonymeter_config.update_data(data)

        self._logger.debug(
            f"Initializing evaluator with method: {self.config['eval_method']}"
        )
        evaluator_class: Any = self.ANONYMETER_CLASS_MAP[
            self.anonymeter_config.eval_method_code
        ]
        self._logger.debug(
            f"Mapped method code: {self.anonymeter_config.eval_method_code}"
        )

        self._impl = evaluator_class(
            **self.anonymeter_config.get_params(
                param_configs=[
                    {attr: {"action": "INCLUDE"}}
                    for attr in self.REQUIRED_ANONYMETER_KEYS_MAP[
                        self.anonymeter_config.eval_method_code
                    ]
                ]
            )
        )

        # catch warnings during synthesizer initialization:
        # UserWarning: Attack is as good or worse as baseline model.
        # FutureWarning: is_categorical_dtype is deprecated and will be removed in a future version.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            attempts_for_impl_evaluate: int = 0
            while attempts_for_impl_evaluate < self.MAX_ATTEMPTS_OF_RUNTIME_ERROR:
                attempts_for_impl_evaluate += 1
                try:
                    self._impl.evaluate(
                        **self.anonymeter_config.get_params(
                            param_configs=[
                                {attr: {"action": "INCLUDE"}}
                                for attr in self.REQUIRED_ANONYMETER_KEYS_EVALUATE_MAP[
                                    self.anonymeter_config.eval_method_code
                                ]
                            ]
                        )
                    )
                    break  # successful
                except RuntimeError:
                    error_msg: str = (
                        f"Evaluating trial {attempts_for_impl_evaluate} / {self.MAX_ATTEMPTS_OF_RUNTIME_ERROR}"
                        " failed due to RunTimeError."
                    )
                    self._logger.warning(error_msg)

                    if attempts_for_impl_evaluate == self.MAX_ATTEMPTS_OF_RUNTIME_ERROR:
                        error_msg = f"Exceeded the maximum number of attempts ({self.MAX_ATTEMPTS_OF_RUNTIME_ERROR}). "
                        self._logger.warning(error_msg)

            for warning in w:
                self._logger.debug(f"Warning during _eval: {warning.message}")

        # self._extract_scores() already handle the exception by assign NA
        anonymeter_scores: dict[str, pd.DataFrame] = self._extract_scores()
        self._logger.debug(f"Extracted scores: {list(anonymeter_scores.keys())}")

        scores: dict[str, pd.DataFrame] = {}
        for granularity in self.AVAILABLE_SCORES_GRANULARITY:
            self._logger.debug(f"Extracting {granularity} level as PETsARD format")

            if granularity == "global":
                scores[granularity] = self._get_global(anonymeter_scores)
            elif granularity == "details":
                scores[granularity] = self._get_details(anonymeter_scores)
        self._logger.info("Successfully extracting scores")

        return scores
