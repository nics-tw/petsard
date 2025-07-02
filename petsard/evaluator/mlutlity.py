import logging
import re
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import f1_score, silhouette_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

from petsard.config_base import BaseConfig
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.metadater.types.data_types import safe_round


class MLUtilityMap(Enum):
    """
    Enumeration for MLUtility method mapping.
    """

    REGRESSION: int = auto()
    CLASSIFICATION: int = auto()
    CLUSTER: int = auto()

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        return cls.__dict__[re.sub(r"^mlutility-", "", method).upper()]


@dataclass
class MLUtilityConfig(BaseConfig):
    """
    Configuration for the MLUtility Evaluator.

    Attributes:
        eval_method: The method name of how you are evaluating data.
        eval_method_code (Optional[int]): The mapped method code.
        target (str, optional):
            The target column for regression/classification.
            Should be a numerical column for regression.
        n_clusters (list[int], optional):
            List of cluster numbers for clustering. Default is [4, 5, 6].
        REQUIRED_INPUT_KEYS (list[str]): The required keys in the input data.
        n_rows (dict[str, int]): Number of rows in each data.
        category_cols (list[str]): List of categorical columns in the data.
        category_cols_cardinality (dict[str, dict[str, int]]):
            Cardinality of categorical columns in the data.
        _logger (logging.Logger): The logger object.
    """

    eval_method: str
    eval_method_code: Optional[int] = None
    target: Optional[str] = None
    n_clusters: list[int] = field(default_factory=lambda: [4, 5, 6])
    REQUIRED_INPUT_KEYS: list[str] = field(
        default_factory=lambda: ["ori", "syn", "control"]
    )
    n_rows: dict[str, int] = field(default_factory=dict)
    category_cols: list[str] = field(default_factory=list)
    category_cols_cardinality: dict[str, dict[str, int]] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        error_msg: Optional[str] = None

        # Map and validate method
        try:
            self.eval_method_code = MLUtilityMap.map(self.eval_method)
        except KeyError:
            error_msg = f"Unsupported method: {self.eval_method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Validate n_clusters
        if not isinstance(self.n_clusters, list):
            error_msg = "n_clusters must be a list of integers"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if not all(isinstance(x, int) for x in self.n_clusters):
            error_msg = "All elements in n_clusters must be integers"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # Validate target for specific methods
        if self.eval_method_code in [
            MLUtilityMap.REGRESSION,
            MLUtilityMap.CLASSIFICATION,
        ]:
            if not self.target:
                error_msg = f"Target column is required for {self.eval_method}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
        elif self.eval_method_code == MLUtilityMap.CLUSTER and self.target is not None:
            self.target = None
            error_msg = (
                "Target column is not required for clustering, input will be ignored"
            )
            self._logger.info(error_msg)

    def update_data(self, data: dict[str, pd.DataFrame]) -> None:
        """
        Validate input data for MLUtility evaluation.

        Args:
            data (Dict[str, pd.DataFrame]): Input data dictionary.

        Raises:
            ConfigError: If data is invalid.
        """
        error_msg: Optional[str] = None

        # Validate required keys
        if not all(key in data for key in self.REQUIRED_INPUT_KEYS):
            error_msg = f"Missing required keys. Expected: {self.REQUIRED_INPUT_KEYS}"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # Validate data is not empty after removing NaNs
        for key in self.REQUIRED_INPUT_KEYS:
            df = data[key].dropna()
            if df.empty:
                error_msg = f"Data for {key} is empty after removing missing values"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

        # Validate target column for regression/classification
        if self.eval_method_code in [
            MLUtilityMap.REGRESSION,
            MLUtilityMap.CLASSIFICATION,
        ]:
            for key in self.REQUIRED_INPUT_KEYS:
                if self.target not in data[key].columns:
                    error_msg = f"Target column '{self.target}' not found in {key} data"
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

        self.n_rows = {key: data[key].shape[0] for key in self.REQUIRED_INPUT_KEYS}
        self._logger.debug(f"Number of rows in each data: {self.n_rows}")

        self.category_cols: list[str] = [
            col
            for col in data["ori"].columns
            if not pd.api.types.is_numeric_dtype(data["ori"][col])
        ]
        self._logger.debug(f"Category columns: {self.category_cols}")
        self.category_cols_cardinality = {
            key: {col: data[key][col].nunique() for col in self.category_cols}
            for key in self.REQUIRED_INPUT_KEYS
        }
        self._logger.debug(
            f"Category columns cardinality: {self.category_cols_cardinality}"
        )


class MLUtility(BaseEvaluator):
    """
    Evaluator for MLUtility method.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn", "control"]
    LOWER_BOUND_MAP: dict[int, float] = {
        MLUtilityMap.CLASSIFICATION: 0.0,
        MLUtilityMap.CLUSTER: -1.0,
        MLUtilityMap.REGRESSION: 0.0,
    }
    AVAILABLE_SCORES_GRANULARITY: list[str] = ["global", "details"]
    HIGH_CARDINALITY_THRESHOLD: float = 0.1  # 1/10 of rows
    RANDOM_STATE_SEED: int = 42

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.

        Attr:
            REQUIRED_INPUT_KEYS (list[str]): The required keys in the input data.
            LOWER_BOUND_MAP (dict[int, float]): The lower bound for the score.
            AVAILABLE_SCORES_GRANULARITY (list[str]): The available scores granularity.
            HIGH_CARDINALITY_THRESHOLD (float):
                The threshold for high cardinality. Represents as percentage of rows.
            RANDOM_STATE_SEED (int): The random state seed for the models.
            _logger (logging.Logger): The logger object.
            config (dict): A dictionary containing the configuration settings.
            mlutility_config (MLUtilityConfig): The configuration object.
            _impl (Optional[dict[str, callable]]): The evaluator object.
                - 'ori': The evaluator object for the original data.
                - 'syn': The evaluator object for the synthetic data.
        """
        super().__init__(config=config)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        self.MLUTILITY_CLASS_MAP: dict[int, callable] = {
            MLUtilityMap.CLASSIFICATION: self._classification,
            MLUtilityMap.CLUSTER: self._cluster,
            MLUtilityMap.REGRESSION: self._regression,
        }

        self._logger.debug(f"Verifying MLUtilityConfig with parameters: {self.config}")
        self.mlutility_config = MLUtilityConfig(**self.config)
        self._logger.debug("MLUtilityConfig successfully initialized")

        self._impl: Optional[dict[str, callable]] = None

    def _preprocessing(
        self, data: dict[str, pd.DataFrame]
    ) -> tuple[dict[str, pd.DataFrame], str]:
        """
        Preprocess the data for the evaluation.
            1. Remove missing values.
            2. Remove high cardinality columns.
            3. One-hot encoding for categorical columns.
            4. Standardize the data.
            5. Check if the target column is constant.

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.

        Returns:
            (tuple[dict[str, pd.DataFrame], str]):
                The preprocessed data and the status of the preprocessing.
                - (dict[str, pd.DataFrame]): The preprocessed data.
                    - (str): key of the data.
                        - X (pd.DataFrame): The feature columns.
                        - y (pd.Series): The target column.
                            Only for regression and classification.
                - (str): The status of the preprocessing.
                    - 'success': The preprocessing is successful.
                    - 'missing_values_cause_empty':
                        The data is empty after removing missing values.
                    - 'target_is_constant':
                        The target column is constant
        """
        error_msg: Optional[str] = None
        inprogress_data: dict[str, pd.DataFrame] = deepcopy(data)
        data_now: Optional[pd.DataFrame] = None
        preprocessed_data: dict[str, pd.DataFrame] = {}

        for key in self.REQUIRED_INPUT_KEYS:
            data_now = inprogress_data[key].copy()
            preprocessed_data[key] = {}

            data_now.dropna(how="any")
            self._logger.debug(f"Missing values removed for {key}")
            if data_now.shape[0] == 0:
                error_msg = f"The data is empty after removing missing values for {key}"
                self._logger.warnings(error_msg)
                return None, "missing_values_cause_empty"

        temp_category_cols: list[str] = (
            [
                col
                for col in self.mlutility_config.category_cols
                if col != self.mlutility_config.target
            ]
            if self.mlutility_config.eval_method_code
            in [
                MLUtilityMap.CLASSIFICATION,
                MLUtilityMap.REGRESSION,
            ]
            else self.mlutility_config.category_cols
        )
        self._logger.debug(
            f"Category columns included: {self.mlutility_config.category_cols}"
        )
        if len(temp_category_cols) != 0:
            for col in self.mlutility_config.category_cols:
                # if the cardinality of the column is too high, remove the column
                if (
                    self.mlutility_config.category_cols_cardinality["ori"][col]
                    >= round(
                        self.mlutility_config.n_rows["ori"]
                        * self.HIGH_CARDINALITY_THRESHOLD
                    )
                ) or (
                    self.mlutility_config.category_cols_cardinality["syn"][col]
                    >= round(
                        self.mlutility_config.n_rows["syn"]
                        * self.HIGH_CARDINALITY_THRESHOLD
                    )
                ):
                    error_msg = (
                        f"The cardinality of the column {col} is too high. "
                        f"Ori: Over row numbers {self.mlutility_config.n_rows['ori']},"
                        f" column cardinality {self.mlutility_config.category_cols_cardinality['ori'][col]}. "
                        f"Syn: Over row numbers {self.mlutility_config.n_rows['syn']},"
                        f" column cardinality {self.mlutility_config.category_cols_cardinality['syn'][col]}. "
                        f"The column {col} is removed."
                    )
                    self._logger.warning(error_msg)
                    temp_category_cols.remove(col)
                    for key in self.REQUIRED_INPUT_KEYS:
                        inprogress_data[key] = inprogress_data[key].drop(
                            columns=col, inplace=False
                        )
                        self._logger.debug(f"Column {col} removed for {key}")

            # One-hot encoding
            ohe = OneHotEncoder(
                drop="first",
                sparse_output=False,
                handle_unknown="infrequent_if_exist",
            )
            ohe.fit(
                pd.concat(
                    [
                        inprogress_data["ori"][temp_category_cols],
                        inprogress_data["syn"][temp_category_cols],
                        inprogress_data["control"][temp_category_cols],
                    ]
                )
            )
            self._logger.debug("One-hot encoding completed")
            for key in self.REQUIRED_INPUT_KEYS:
                data_now = inprogress_data[key].copy()
                data_now = pd.DataFrame(
                    ohe.transform(data_now[temp_category_cols]),
                    columns=ohe.get_feature_names_out(temp_category_cols),
                    index=data_now.index,
                )
                inprogress_data[key] = inprogress_data[key].drop(
                    columns=temp_category_cols,
                    inplace=False,
                )
                inprogress_data[key] = pd.concat(
                    [inprogress_data[key], data_now], axis=1
                )
                self._logger.debug(f"One-hot encoding completed for {key}")

        if self.mlutility_config.eval_method_code in [
            MLUtilityMap.CLASSIFICATION,
            MLUtilityMap.REGRESSION,
        ]:
            target: str = self.mlutility_config.target

            if self.mlutility_config.eval_method_code == MLUtilityMap.REGRESSION:
                ss_y = StandardScaler()
                ss_y.fit(
                    np.concatenate(
                        [
                            inprogress_data["ori"][target].values.reshape(-1, 1),
                            inprogress_data["syn"][target].values.reshape(-1, 1),
                            inprogress_data["control"][target].values.reshape(-1, 1),
                        ]
                    )
                )
            ss_X = StandardScaler()
            ss_X.fit(
                pd.concat(
                    [
                        inprogress_data["ori"].drop(columns=[target], inplace=False),
                        inprogress_data["syn"].drop(columns=[target], inplace=False),
                        inprogress_data["control"].drop(
                            columns=[target], inplace=False
                        ),
                    ]
                )
            )

            for key in self.REQUIRED_INPUT_KEYS:
                target_value: np.ndarray = inprogress_data[key][target].values

                # check if the target is constant
                if len(np.unique(target_value)) == 1:
                    error_msg = f"The target column '{target}' is constant."
                    self._logger.warning(error_msg)
                    return None, "target_is_constant"

                preprocessed_data[key]["y"] = (
                    ss_y.transform(target_value.reshape(-1, 1)).ravel()
                    if self.mlutility_config.eval_method_code == MLUtilityMap.REGRESSION
                    else target_value
                )
                preprocessed_data[key]["X"] = ss_X.transform(
                    inprogress_data[key].drop(columns=[target], inplace=False)
                )

        elif self.mlutility_config.eval_method_code == MLUtilityMap.CLUSTER:
            united_columns = list(
                set(
                    inprogress_data["ori"].columns.tolist()
                    + inprogress_data["syn"].columns.tolist()
                    + inprogress_data["control"].columns.tolist()
                )
            )

            ss = StandardScaler()
            ss.fit(
                pd.concat(
                    [
                        inprogress_data["ori"].reindex(
                            columns=united_columns, fill_value=0.0
                        ),
                        inprogress_data["syn"].reindex(
                            columns=united_columns, fill_value=0.0
                        ),
                        inprogress_data["control"].reindex(
                            columns=united_columns, fill_value=0.0
                        ),
                    ],
                    axis=0,
                )
            )

            for key in self.REQUIRED_INPUT_KEYS:
                preprocessed_data[key] = {}
                preprocessed_data[key]["X"] = ss.transform(
                    inprogress_data[key].reindex(
                        columns=united_columns, fill_value=0.0
                    ),
                )

        self._logger.debug(
            f"Encoding and standardization of {self.mlutility_config.eval_method} completed"
        )

        self._logger.debug(
            f"Data preprocessing of {self.mlutility_config.eval_method} completed"
        )

        return preprocessed_data, "success"

    def _adjust_to_lower_bound(self, value: float) -> float:
        """
        Check if the score is beyond the lower bound.
            If the score is less than the lower bound, return the lower bound.
             Otherwise, return the value.
            - For regression and classification, the lower bound is 0.
            - For clustering, the lower bound is -1.

        Args:
            value (float): The value to be checked.
            type (str): The type of the evaluation.

        Returns:
            (float): The value in the range.
        """
        error_msg: Optional[str] = None
        lower_bound: float = self.LOWER_BOUND_MAP[
            self.mlutility_config.eval_method_code
        ]

        if value < lower_bound:
            error_msg = (
                f"The score {value} is less than the lower bound, "
                "indicating the performance is arbitrarily poor. "
                "So the score is set to the lower bound."
            )
            self._logger.warning(error_msg)
            value = lower_bound

        return value

    def _classification(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> dict[str, float]:
        """
        Classification model fitting, evaluation, and testing.
            The models used are logistic regression, SVC, random forest, and gradient boosting.

        The metric used for evaluation is f1 score.

        Args:
            X_train (np.ndarray): The data to be fitted.
            y_train (np.ndarray): The target column of the training data.
            X_test (np.ndarray): The data to be tested.
            y_test (np.ndarray): The target column of the testing data.

        Returns:
            (dict[str, float]): The result of the evaluation.
                - 'logistic_regression': The f1 score of the logistic regression model.
                - 'svc': The f1 score of the SVC model.
                - 'random_forest': The f1 score of the random forest model.
                - 'gradient_boosting': The f1 score of the gradient boosting model
        """
        result: dict[str, float] = {}
        average_method: str = "micro"

        models_to_evaluate_map: dict[str, callable] = {
            "logistic_regression": LogisticRegression(
                random_state=self.RANDOM_STATE_SEED
            ),
            "svc": SVC(random_state=self.RANDOM_STATE_SEED),
            "random_forest": RandomForestClassifier(
                random_state=self.RANDOM_STATE_SEED
            ),
            "gradient_boosting": GradientBoostingClassifier(
                random_state=self.RANDOM_STATE_SEED
            ),
        }

        # train
        for model in models_to_evaluate_map.values():
            model.fit(X_train, y_train)

        # evaluate
        result = {
            name: f1_score(
                y_test,
                model.fit(X_train, y_train).predict(X_test),
                average=average_method,
            )
            for name, model in models_to_evaluate_map.items()
        }

        return result

    def _cluster(self, X_train: np.ndarray, X_test: np.ndarray) -> dict[str, float]:
        """
        Clustering model fitting, evaluation, and testing.
            The models used are KMeans with different number of clusters.
            For the robustness of the results,
                the model is trained and evaluated 5 times,
                and the average of the results is used as the final result.

        The metric used for evaluation is silhouette score.

        Args:
            X_train (pd.DataFrame): The data to be fitted.
            X_test (pd.DataFrame): The data to be tested.
            n_clusters (list): A list of numbers of clusters for clustering.

        Returns:
            result (dict): The result of the evaluation.
        """
        silhouette_score_value: float = None
        result: dict[str, float] = {}

        for k in self.mlutility_config.n_clusters:
            k_model = KMeans(
                random_state=self.RANDOM_STATE_SEED, n_clusters=k, n_init="auto"
            )

            k_model.fit(X_train)

            try:
                silhouette_score_value = silhouette_score(
                    X_test, k_model.predict(X_test)
                )
            except ValueError as e:
                error_msg: str = (
                    "There is only one cluster in the prediction, "
                    "or the valid data samples are too few, "
                    "indicating the performance is arbitrarily poor. "
                    "The score is set to the lower bound."
                    f"Error message: {str(e)}"
                )
                self._logger.warning(error_msg)
                silhouette_score_value = -1

            result[f"KMeans_cluster{k}"] = self._adjust_to_lower_bound(
                silhouette_score_value,
            )

        return result

    def _regression(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> dict[str, float]:
        """
        Regression model fitting, evaluation, and testing.
            The models used are linear regression, random forest, and gradient boosting.

        The metric used for evaluation is R^2.

        Args:
            X_train (np.ndarray): The data to be fitted.
            y_train (np.ndarray): The target column of the training data.
            X_test (np.ndarray): The data to be tested.
            y_test (np.ndarray): The target column of the testing data.

        Returns:
            (dict[str, float]): The result of the evaluation.
                - 'linear_regression': The R^2 score of the linear regression model.
                - 'random_forest': The R^2 score of the random forest model.
                - 'gradient_boosting': The R^2 score of the gradient boosting model
        """
        result: dict[str, float] = {}

        models_to_evaluate_map: dict[str, callable] = {
            "linear_regression": LinearRegression(),
            "random_forest": RandomForestRegressor(random_state=self.RANDOM_STATE_SEED),
            "gradient_boosting": GradientBoostingRegressor(
                random_state=self.RANDOM_STATE_SEED
            ),
        }

        result = {
            name: self._adjust_to_lower_bound(
                model.fit(X_train, y_train).score(X_test, y_test)
            )
            for name, model in models_to_evaluate_map.items()
        }

        return result

    def _get_global(
        self, result: dict[str, Optional[dict[str, float]]]
    ) -> pd.DataFrame:
        """
        Get the global result of the evaluation.

        Args:
            result (dict[str, Optional[dict[str, float]]]): The evaluation result
                - 'ori': The evaluation result of the original data.
                - 'syn': The evaluation result of the synthetic data.

        Returns:
            (pd.DataFrame): The global result of the evaluation.
        """
        ori_value: list[float] = list(result.get("ori", {}).values() or [0])
        syn_value: list[float] = list(result.get("syn", {}).values() or [0])

        compare_df: pd.DataFrame = pd.DataFrame(
            {
                "ori_mean": safe_round(np.mean(ori_value)),
                "ori_std": safe_round(np.std(ori_value)),
                "syn_mean": safe_round(np.mean(syn_value)),
                "syn_std": safe_round(np.std(syn_value)),
            },
            index=[0],
        )

        compare_df["diff"] = safe_round(compare_df["syn_mean"] - compare_df["ori_mean"])

        return compare_df

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict:
        """
        Evaluate the data with the method given in the config.

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.

        Returns:
            (dict) he evaluation result.
        """
        preprocessed_data: dict[str, pd.DataFrame] = {}
        result_details: dict[str, Optional[dict[str, float]]] = {}

        self.mlutility_config.update_data(data)

        preprocessed_data, status = self._preprocessing(data)
        self._logger.debug("Data preprocessing completed")
        if status in ("missing_values_cause_empty", "target_is_constant"):
            self._logger.warning(
                f"Evaluator Preprocessing status: {status}, result will be NaN"
            )
            result_details = {
                "ori": {"error": np.nan},
                "syn": {"error": np.nan},
            }
        else:
            self._logger.debug(
                f"Initializing evaluator with method: {self.config['eval_method']}"
            )
            evaluator_class: Any = self.MLUTILITY_CLASS_MAP[
                self.mlutility_config.eval_method_code
            ]
            self._logger.debug(
                f"Mapped method code: {self.mlutility_config.eval_method_code}"
            )
            self._impl = {"ori": evaluator_class, "syn": evaluator_class}

            result_details = {
                data_type: evaluator_class(
                    **(
                        dict(
                            X_train=preprocessed_data[data_type]["X"],
                            y_train=preprocessed_data[data_type]["y"],
                            X_test=preprocessed_data["control"]["X"],
                            y_test=preprocessed_data["control"]["y"],
                        )
                        if self.mlutility_config.eval_method_code
                        in [MLUtilityMap.CLASSIFICATION, MLUtilityMap.REGRESSION]
                        else dict(
                            X_train=preprocessed_data[data_type]["X"],
                            X_test=preprocessed_data["control"]["X"],
                        )
                    )
                )
                for data_type in ["ori", "syn"]
            }

        return {
            "global": self._get_global(result_details),
            "details": result_details,
        }
