import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

import pandas as pd

from petsard.config_base import BaseConfig
from petsard.evaluator.data_describer_base import (
    DataDescriberColNA,
    DataDescriberColumnCount,
    DataDescriberCorr,
    DataDescriberCov,
    DataDescriberGlobalNA,
    DataDescriberKurtosis,
    DataDescriberMax,
    DataDescriberMean,
    DataDescriberMedian,
    DataDescriberMin,
    DataDescriberNUnique,
    DataDescriberPercentile,
    DataDescriberQ1,
    DataDescriberQ3,
    DataDescriberRowCount,
    DataDescriberSkew,
    DataDescriberStd,
    DataDescriberVar,
)
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.metadater import safe_round


class DataDescriberMap(Enum):
    """
    Mapping of the describing method to the corresponding code.
    """

    ROW_COUNT: int = auto()
    COL_COUNT: int = auto()
    GLOBAL_NA_COUNT: int = auto()
    MENA: int = auto()
    MEDIAN: int = auto()
    STD: int = auto()
    VAR: int = auto()
    MIN: int = auto()
    MAX: int = auto()
    KURTOSIS: int = auto()
    SKEW: int = auto()
    Q1: int = auto()
    Q3: int = auto()
    IQR: int = auto()
    RANGE: int = auto()
    PERCENTILE: int = auto()
    COL_NA_COUNT: int = auto()
    NUNIUQE: int = auto()
    COV: int = auto()
    CORR: int = auto()

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        return cls.__dict__[method.upper()]


@dataclass
class DataDescriberConfig(BaseConfig):
    """
    Configuration for the Stats Evaluator.

    Attributes:
        eval_method (str): The evaluation method.
        eval_method_code (int): The evaluation method code.
        describe_method (list[str]): The list of describing methods.
    """

    eval_method: str
    eval_method_code: Optional[int] = None

    AVAILABLE_DESCRIBE_METHODS: list[str] = field(
        default_factory=lambda: [
            "row_count",
            "col_count",
            "global_na_count",
            "mean",
            "median",
            "std",
            "var",
            "min",
            "max",
            "kurtosis",
            "skew",
            "q1",
            "q3",
            "percentile",
            "col_na_count",
            "nunique",
            "corr",
            "cov",
        ]
    )
    REQUIRED_INPUT_KEYS: list[str] = field(default_factory=lambda: ["data"])

    describe_method: str | list[str] = field(
        default_factory=lambda: [
            "row_count",
            "col_count",
            "global_na_count",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "kurtosis",
            "skew",
            "q1",
            "q3",
            "col_na_count",
            "nunique",
            "corr",
        ]
    )
    percentile: int | float = None

    def __post_init__(self):
        super().__post_init__()
        error_msg: Optional[str] = None

        if isinstance(self.describe_method, str):
            self.describe_method = [self.describe_method]

        invalid_methods: list[str] = [
            method
            for method in self.describe_method
            if method not in self.AVAILABLE_DESCRIBE_METHODS
        ]
        if invalid_methods:
            error_msg = (
                f"Invalid describe method: {invalid_methods}. "
                f"Available methods are: {self.AVAILABLE_DESCRIBE_METHODS}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if "percentile" not in self.describe_method:
            self.percentile = None
            self._logger.debug(
                "Percentile method is not in describe_method, "
                "setting percentile to None"
            )

    def update_data(self, data: dict[str, pd.DataFrame]) -> None:
        error_msg: Optional[str] = None

        self._logger.info(
            f"Updating data with {len(self.REQUIRED_INPUT_KEYS)} required keys"
        )

        # Validate required keys
        if not all(key in data for key in self.REQUIRED_INPUT_KEYS):
            error_msg = f"Missing required keys. Expected: {self.REQUIRED_INPUT_KEYS}"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)


class DataDescriber(BaseEvaluator):
    """
    Evaluator for Desciber method.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["data"]
    EXEC_GRANULARITY_MAP: dict[str, str] = {
        method: granularity
        for granularity, methods in {
            "global": [
                "row_count",
                "col_count",
                "global_na_count",
            ],
            "columnwise": [
                "mean",
                "median",
                "std",
                "var",
                "min",
                "max",
                "kurtosis",
                "skew",
                "q1",
                "q3",
                "iqr",
                "range",
                "percentile",
                "nunique",
                "col_na_count",
            ],
            "pairwise": [
                "cov",
                "corr",
            ],
        }.items()
        for method in methods
    }
    MODULE_MAP: dict[str, callable] = {
        "row_count": DataDescriberRowCount,
        "col_count": DataDescriberColumnCount,
        "global_na_count": DataDescriberGlobalNA,
        "mean": DataDescriberMean,
        "median": DataDescriberMedian,
        "std": DataDescriberStd,
        "var": DataDescriberVar,
        "min": DataDescriberMin,
        "max": DataDescriberMax,
        "kurtosis": DataDescriberKurtosis,
        "skew": DataDescriberSkew,
        "q1": DataDescriberQ1,
        "q3": DataDescriberQ3,
        "percentile": DataDescriberPercentile,
        "col_na_count": DataDescriberColNA,
        "nunique": DataDescriberNUnique,
        "corr": DataDescriberCorr,
        "cov": DataDescriberCov,
    }
    INT_MODULE: list[str] = [
        "row_count",
        "col_count",
        "global_na_count",
        "col_na_count",
        "nunique",
    ]
    AVAILABLE_SCORES_GRANULARITY: list[str] = ["global", "columnwise", "pairwise"]

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration assign by Evaluator.

        Attributes:
            REQUIRED_INPUT_KEYS (list[str]): The required input keys.
            AVAILABLE_SCORES_GRANULARITY (list[str]): The available scores granularity.
            _logger (logging.Logger): The logger object.
            desc_config (StatsConfig): The configuration parameters for the describing evaluator.
            _impl (Optional[dict[str, callable]]): The implementation object.
        """
        super().__init__(config=config)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        self._logger.debug(f"Verifying StatsConfig with parameters: {self.config}")
        self.desc_config = DataDescriberConfig(**self.config)
        self._logger.debug("StatsConfig successfully initialized")

        impl_config: dict[str, Any] = self.config
        _ = impl_config.pop("eval_method", None)
        self._impl: Optional[dict[str, callable]] = {
            method: self.MODULE_MAP[method](config=impl_config)
            for method in self.desc_config.describe_method
        }

    def _get_columnwise(self, columnwise_desc: list[Any]) -> pd.DataFrame:
        columnwise_desc_df: pd.DataFrame = pd.DataFrame(
            {k: v for d in columnwise_desc for k, v in d.items()}
        )

        for col in columnwise_desc_df.columns:
            if col in self.INT_MODULE:
                columnwise_desc_df[col] = (
                    columnwise_desc_df[col].fillna(-1).astype(int).replace(-1, pd.NA)
                )
            else:
                # 安全處理 safe_round 可能返回 None 的情況
                rounded_series = columnwise_desc_df[col].apply(safe_round)
                columnwise_desc_df[col] = rounded_series.fillna(pd.NA)

        return columnwise_desc_df

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the describer.
            _impl should be initialized in this method.

        Args:
            data (dict[str, pd.DataFrame]): The data to be described.

        Return:
            (dict[str, pd.DataFrame]): The describe result
        """
        error_msg: str = None
        self._logger.info(
            f"Starting evaluation with {len(self.desc_config.describe_method)} statistical methods"
        )
        self.desc_config.update_data(data)

        # Assign to list first, convert to DataFrame later
        temp_desc_result: dict[str, list[Any]] = {}
        granularity: str = None
        for method in self.desc_config.describe_method:
            self._logger.info(f"Describing data with method: {method}")

            try:
                granularity = self.EXEC_GRANULARITY_MAP[method]
            except KeyError:
                error_msg: str = f"Unassigned granulariy describer method: {method}"
                self._logger.error(error_msg)
                raise UnsupportedMethodError(error_msg)
            if granularity not in temp_desc_result:
                temp_desc_result[granularity] = []

            temp_desc_result[granularity].append(self._impl[method].eval(data["data"]))

        desc_result: dict[str, pd.DataFrame] = {}
        if "global" in temp_desc_result:
            desc_result["global"] = pd.DataFrame(
                [{k: v for d in temp_desc_result["global"] for k, v in d.items()}]
            )
        if "columnwise" in temp_desc_result:
            desc_result["columnwise"] = self._get_columnwise(
                temp_desc_result["columnwise"]
            )
        if "pairwise" in temp_desc_result:
            temp_df: pd.DataFrame = pd.DataFrame(
                [
                    (col1, col2, metric, value)
                    for d in temp_desc_result["pairwise"]
                    for metric, pairs in d.items()
                    for (col1, col2), value in pairs.items()
                ],
                columns=["column1", "column2", "metric", "value"],
            ).reset_index(drop=True)

            temp_df = temp_df.pivot(
                index=["column1", "column2"], columns="metric", values="value"
            ).reset_index()
            temp_df.columns.name = None
            desc_result["pairwise"] = temp_df.copy()

        return desc_result
