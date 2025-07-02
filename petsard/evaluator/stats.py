import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

import numpy as np
import pandas as pd

from petsard.config_base import BaseConfig
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.evaluator.stats_base import (
    StatsJSDivergence,
    StatsMax,
    StatsMean,
    StatsMedian,
    StatsMin,
    StatsNUnique,
    StatsStd,
)
from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.metadater import Metadater, safe_round


class StatsMap(Enum):
    """
    Mapping of the statistics method to the corresponding code.
    """

    MEAN = auto()
    STD = auto()
    MEDIAN = auto()
    MIN = auto()
    MAX = auto()
    NUNIQUE = auto()
    JSDIVERGENCE = auto()

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value
            Accept both of "sdmetrics-" or "sdmetrics-single_table-" prefix

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        return cls.__dict__[method.upper()]


@dataclass
class StatsConfig(BaseConfig):
    """
    Configuration for the Stats Evaluator.

    Attributes:
        eval_method (str): The evaluation method.
        eval_method_code (int): The evaluation method code.
        AVALIABLE_STATS_METHODS (list[str]): The available statistics methods.
        AVAILABLE_COMPARE_METHODS (list[str]): The available compare methods.
        AVAILABLE_AGGREGATED_METHODS (list[str]): The available aggregated methods.
        AVAILABLE_SUMMARY_METHODS (list[str]): The available summary methods.
        REQUIRED_INPUT_KEYS (list[str]): The required input keys.
        stats_method (list[str]): The statistics methods.
        compare_method (str): The compare method.
        aggregated_method (str): The aggregated method.
        summary_method (str): The summary method.
        columns_info (dict): The columns information.
            - ori/syn_dtype (str): The data type of the column.
            - ori/syn_infer_dtype (str): The inferred data type of the column.
            - dtype_match (bool): Whether the data type matches.
            - infer_dtype_match (bool): Whether the inferred data type matches.

    """

    eval_method: str
    eval_method_code: Optional[int] = None
    AVAILABLE_STATS_METHODS: list[str] = field(
        default_factory=lambda: [
            "mean",
            "std",
            "median",
            "min",
            "max",
            "nunique",
            "jsdivergence",
        ]
    )
    AVAILABLE_COMPARE_METHODS: list[str] = field(
        default_factory=lambda: ["diff", "pct_change"]
    )
    AVAILABLE_AGGREGATED_METHODS: list[str] = field(default_factory=lambda: ["mean"])
    AVAILABLE_SUMMARY_METHODS: list[str] = field(default_factory=lambda: ["mean"])
    REQUIRED_INPUT_KEYS: list[str] = field(default_factory=lambda: ["ori", "syn"])
    stats_method: list[str] = field(
        default_factory=lambda: [
            "mean",
            "std",
            "median",
            "min",
            "max",
            "nunique",
            "jsdivergence",
        ]
    )
    compare_method: str = "pct_change"
    aggregated_method: str = "mean"
    summary_method: str = "mean"
    columns_info: Optional[dict[str, dict[str, str]]] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        error_msg: Optional[str] = None

        invalid_methods: list[str] = [
            method
            for method in self.stats_method
            if method not in self.AVAILABLE_STATS_METHODS
        ]
        if invalid_methods:
            error_msg = (
                f"Invalid stats method: {invalid_methods}. "
                f"Available methods are: {self.AVAILABLE_STATS_METHODS}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if self.compare_method not in self.AVAILABLE_COMPARE_METHODS:
            error_msg = f"Invalid compare method: {self.compare_method}."
            self._looger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if self.aggregated_method not in self.AVAILABLE_AGGREGATED_METHODS:
            error_msg = f"Invalid aggregated method: {self.aggregated_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if self.summary_method not in self.AVAILABLE_SUMMARY_METHODS:
            error_msg = f"Invalid summary method: {self.summary_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

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

        ori_colnames: list[str] = data["ori"].columns
        syn_colnames: list[str] = data["syn"].columns
        colnames = list(set(ori_colnames) & set(syn_colnames))
        self._logger.debug(
            f"Found {len(colnames)} common columns between original and synthetic data"
        )

        self.columns_info = {}
        temp: dict[str, str] = None
        dtype = None
        for colname in colnames:
            temp = {}

            for source in ["ori", "syn"]:
                if colname in data[source].columns:
                    dtype = data[source][colname].dtype
                    # Create a temporary series to analyze the data type
                    temp_series = data[source][colname]
                    field_metadata = Metadater.create_field(
                        series=temp_series,
                        field_name=colname,
                        compute_stats=False,
                        infer_logical_type=False,
                        optimize_dtype=False,
                    )
                    temp.update(
                        {
                            f"{source}_dtype": dtype,
                            f"{source}_infer_dtype": field_metadata.data_type.value.lower(),
                        }
                    )
            temp["dtype_match"] = temp.get("ori_dtype") == temp.get("syn_dtype")
            temp["infer_dtype_match"] = temp.get("ori_infer_dtype") == temp.get(
                "syn_infer_dtype"
            )
            self.columns_info[colname] = temp
        self._logger.debug(
            f"Column information updated for {len(self.columns_info)} columns"
        )


class Stats(BaseEvaluator):
    """
    Evaluator for Statistics method.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn"]
    INFER_DTYPE_MAP: dict[str, str] = {
        method: dtype
        for dtype, methods in {
            "numerical": [
                "mean",
                "std",
                "median",
                "min",
                "max",
            ],
            "categorical": ["nunique", "jsdivergence"],
        }.items()
        for method in methods
    }
    EXEC_GRANULARITY_MAP: dict[str, str] = {
        method: granularity
        for granularity, methods in {
            "columnwise": [
                "mean",
                "std",
                "median",
                "min",
                "max",
                "nunique",
            ],
            "percolumn": [
                "jsdivergence",
            ],
        }.items()
        for method in methods
    }
    MODULE_MAP: dict[str, callable] = {
        "mean": StatsMean,
        "std": StatsStd,
        "median": StatsMedian,
        "min": StatsMin,
        "max": StatsMax,
        "nunique": StatsNUnique,
        "jsdivergence": StatsJSDivergence,
    }
    COMPARE_METHOD_MAP: dict[str, dict[str, callable]] = {
        "diff": {
            "func": lambda syn, ori: syn - ori,
            "handle_zero": lambda syn, ori: syn - ori,
        },
        "pct_change": {
            "func": lambda syn, ori: (syn - ori) / abs(ori),
            "handle_zero": lambda syn, ori: np.nan,
        },
    }
    AGGREGATED_METHOD_MAP: dict[str, callable] = {
        "mean": lambda df: {k: safe_round(v) for k, v in df.mean().to_dict().items()}
    }
    SUMMARY_METHOD_MAP: dict[str, callable] = {
        "mean": lambda values: safe_round(np.mean(list(values)))
    }
    AVAILABLE_SCORES_GRANULARITY: list[str] = ["global", "columnwise"]  # "pairwise"

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration assign by Evaluator.
        """
        super().__init__(config=config)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        self._logger.debug(f"Verifying StatsConfig with parameters: {self.config}")
        self.stats_config = StatsConfig(**self.config)
        self._logger.debug("StatsConfig successfully initialized")

        self._impl: Optional[dict[str, callable]] = None

    def _process_columnwise(
        self, data: dict[str, pd.DataFrame], col: str, info: dict[str, Any], method: str
    ) -> dict[str, float]:
        """
        Process column-wise statistics and return updated result

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.
            col (str): Column name
            info (dict[str, Any]): Column information
            method (str): Statistical method name

        Returns:
            (dict[str, float]) Updated column result
        """
        infer_type: list[str] = self.INFER_DTYPE_MAP[method]
        module: callable = self.MODULE_MAP[method]

        result: dict[str, float] = {}
        if info["infer_dtype_match"] and info["ori_infer_dtype"] in infer_type:
            self._logger.debug(
                f"Column '{col}' data type matches required type for method '{method}'"
            )
            for source in ["ori", "syn"]:
                result[f"{method}_{source}"] = module().eval(
                    data={"col": data[source][col]}
                )
        else:
            self._logger.debug(
                f"Column '{col}' data type does not match required type for method '{method}', returning NaN"
            )
            result[f"{method}_ori"] = np.nan
            result[f"{method}_syn"] = np.nan

        return result

    def _process_percolumn(
        self, data: dict[str, pd.DataFrame], col: str, info: dict[str, Any], method: str
    ) -> dict[str, float]:
        """
        Process per-column statistics and return updated result

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.
            col (str): Column name
            info (dict[str, Any]): Column information
            method (str): Statistical method name

        Returns:
            (dict[str, float]) Updated column result
        """
        self._logger.debug(
            f"Processing per-column statistics for column '{col}' using method '{method}'"
        )

        infer_type: list[str] = self.INFER_DTYPE_MAP[method]
        module: callable = self.MODULE_MAP[method]

        result: dict[str, float] = {}
        if info["infer_dtype_match"] and info["ori_infer_dtype"] in infer_type:
            result[method] = module().eval(
                {
                    "col_ori": data["ori"][col],
                    "col_syn": data["syn"][col],
                }
            )
        else:
            result[method] = np.nan

        return result

    def process_pairwise(
        self,
        data: dict[str, pd.DataFrame],
        col1: str,
        info1: dict[str, Any],
        col2: str,
        info2: dict[str, Any],
        method: str,
    ) -> dict[str, float]:
        """
        Process pairwise statistics and return updated result

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.
            col1 (str): First column name
            info1 (dict[str, Any]: First column information
            col2 (str): Second column name
            info2 (dict[str, Any]): Second column information
            method (str): Statistical method name

        Returns:
            (dict[str, float]): Updated pair result
        """
        infer_type = self.INFER_DTYPE_MAP[method]
        module = self.MODULE_MAP[method]

        result = {}
        # Process original data
        if (
            info1["ori_infer_dtype"] in infer_type
            and info2["ori_infer_dtype"] in infer_type
        ):
            result[f"{method}_ori"] = module().eval(
                {
                    "col1": data["ori"][col1],
                    "col2": data["ori"][col2],
                }
            )
        else:
            result[f"{method}_ori"] = np.nan

        # Process synthetic data
        if (
            info1["syn_infer_dtype"] in infer_type
            and info2["syn_infer_dtype"] in infer_type
        ):
            result[f"{method}_syn"] = module().eval(
                {
                    "col1": data["syn"][col1],
                    "col2": data["syn"][col2],
                }
            )
        else:
            result[f"{method}_syn"] = np.nan

        return result

    def _apply_comparison(self, df: pd.DataFrame, compare_method: str) -> pd.DataFrame:
        """
        Apply comparison method to DataFrame

        Args:
            df (pd.DataFrame): The DataFrame to be compared
            compare_method (str): The comparison method
        """
        self._logger.debug(
            f"Applying comparison method '{compare_method}' to DataFrame"
        )
        error_msg: Optional[list[str]] = None

        method_info = self.COMPARE_METHOD_MAP.get(compare_method)
        if not method_info:
            error_msg = f"Unsupported comparison method: {compare_method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        ori_cols: list[str] = [col for col in df.columns if col.endswith("_ori")]
        syn_cols: list[str] = [col.replace("_ori", "_syn") for col in ori_cols]
        self._logger.debug(f"Found {len(ori_cols)} original columns for comparison")

        if not all(col in df.columns for col in syn_cols):
            error_msg = "Missing synthetic columns"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        result = df.copy()
        for ori_col, syn_col in zip(ori_cols, syn_cols):
            eval_col = f"{ori_col.replace('_ori', f'_{compare_method}')}"

            if eval_col in result.columns:
                result.drop(columns=[eval_col], inplace=True)

            result.insert(result.columns.get_loc(syn_col) + 1, eval_col, np.nan)

            # Apply appropriate function based on whether original value is zero
            func = method_info["func"]
            handle_zero = method_info["handle_zero"]
            result[eval_col] = np.where(
                result[ori_col].astype(float) == 0.0,
                handle_zero(result[syn_col], result[ori_col]),
                safe_round(func(result[syn_col], result[ori_col])),
            )

        self._logger.debug(f"Comparison method '{compare_method}' applied successfully")
        return result

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the evaluator.
            _impl should be initialized in this method.

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.

        Return:
            (dict[str, pd.DataFrame]): The evaluation result
        """
        self._logger.info(
            f"Starting evaluation with {len(self.stats_config.stats_method)} statistical methods"
        )
        self.stats_config.update_data(data)

        columns_results: dict[str, dict[str, float]] = {}
        pairs_results: dict[str, dict[str, float]] = {}
        # Process each column
        for col1, info1 in self.stats_config.columns_info.items():
            columns_results[col1] = {}

            # Process each statistical method
            for method in self.stats_config.stats_method:
                exec_granularity = self.EXEC_GRANULARITY_MAP[method]

                # Update results based on granularity
                if exec_granularity == "columnwise":
                    columns_results[col1].update(
                        self._process_columnwise(data, col1, info1, method)
                    )
                elif exec_granularity == "percolumn":
                    columns_results[col1].update(
                        self._process_percolumn(data, col1, info1, method)
                    )
        self._logger.debug(f"Processed statistics for {len(columns_results)} columns")

        # Process pairwise statistics separately to avoid duplication
        for method in self.stats_config.stats_method:
            if self.EXEC_GRANULARITY_MAP[method] == "pairwise":
                column_items = list(self.stats_config.columns_info.items())
                for i in range(len(column_items)):
                    col1, info1 = column_items[i]
                    for j in range(i + 1, len(column_items)):
                        col2, info2 = column_items[j]
                        pairs_key = (col1, col2)
                        if pairs_key not in pairs_results:
                            pairs_results[pairs_key] = {}
                        pairs_results[pairs_key].update(
                            self._process_pairwise(
                                data, col1, info1, col2, info2, method
                            )
                        )
        if pairs_results:
            self._logger.debug(
                f"Processed pair-wise statistics for {len(pairs_results)} column pairs"
            )

        stats_result: dict[str, pd.DataFrame] = {}
        if columns_results:
            stats_result["columnwise"] = pd.DataFrame(columns_results).T
        if pairs_results:
            stats_result["pairwise"] = pd.DataFrame(pairs_results).T

        # Compare, Aggregated, and Summary results
        compare_method: str = self.stats_config.compare_method
        aggregated_method: str = self.stats_config.aggregated_method
        summary_method: str = self.stats_config.summary_method

        compare_col: list[str] = []
        global_result: dict[str, float] = {}
        for granularity in ["columnwise", "pairwise"]:
            if granularity in stats_result and stats_result is not None:
                # Apply comparison method
                stats_result[granularity] = self._apply_comparison(
                    stats_result[granularity], compare_method
                )
                self._logger.debug(
                    f"Applied comparison method '{compare_method}' to results"
                )

                compare_col = [
                    col
                    for col in stats_result[granularity]
                    if col.endswith(f"_{compare_method}")
                ]
                # add aggregated percolumn method
                compare_col += [
                    stats_method
                    for stats_method in self.stats_config.stats_method
                    if self.EXEC_GRANULARITY_MAP[stats_method] == "percolumn"
                ]

                # Apply aggregated method
                global_result.update(
                    self.AGGREGATED_METHOD_MAP[aggregated_method](
                        stats_result[granularity][compare_col]
                    )
                )

        # Apply summary method
        score: float = self.SUMMARY_METHOD_MAP[summary_method](global_result.values())
        global_result = {"Score": score, **global_result}
        stats_result["global"] = pd.DataFrame.from_dict(global_result, orient="index").T
        self._logger.info(f"Evaluation completed with global score: {score:.4f}")
        return stats_result
