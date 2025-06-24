import logging
from abc import abstractmethod
from typing import Any, Optional

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_object_dtype, is_string_dtype

from petsard.exceptions import ConfigError


class BaseDataDescriber:
    """
    Base class for describers.
    """

    def __init__(self, config: dict[str, Any] = None):
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.debug(f"Initializing {self.__class__.__name__}")

        self.config = self._init_config(config)
        self._logger.debug(f"Configuration: {self.config}")

    def _init_config(self, config: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Initialize the configuration parameters.

        Designed to be overridden by subclasses to customize initialization logic.
        """
        return None

    def eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return self._eval(data)

    @abstractmethod
    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        error_msg: str = "eval method not implemented in BaseDataDescriber"
        self._logger.error(error_msg)
        raise NotImplementedError(error_msg)


class DataDescriberRowCount(BaseDataDescriber):
    """
    Calculate the number of rows in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"row_count": int(data.shape[0])}


class DataDescriberColumnCount(BaseDataDescriber):
    """
    Calculate the number of columns in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"col_count": int(data.shape[1])}


class DataDescriberGlobalNA(BaseDataDescriber):
    """
    Calculate the number of rows with NA in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"na_count": int(data.isna().any(axis=1).sum())}


class DataDescriberMean(BaseDataDescriber):
    """
    Calculate the mean of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"mean": data.mean(axis=0, numeric_only=True).to_dict()}


class DataDescriberMedian(BaseDataDescriber):
    """
    Calculate the median of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"median": data.median(axis=0, numeric_only=True).to_dict()}


class DataDescriberStd(BaseDataDescriber):
    """
    Calculate the standard deviation of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"std": data.std(axis=0, numeric_only=True).to_dict()}


class DataDescriberVar(BaseDataDescriber):
    """
    Calculate the variance of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"var": data.var(axis=0, numeric_only=True).to_dict()}


class DataDescriberMin(BaseDataDescriber):
    """
    Calculate the minimum of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"min": data.min(axis=0, numeric_only=True).to_dict()}


class DataDescriberMax(BaseDataDescriber):
    """
    Calculate the maximum of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"max": data.max(axis=0, numeric_only=True).to_dict()}


class DataDescriberKurtosis(BaseDataDescriber):
    """
    Calculate the kurtosis of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"kurtosis": data.kurt(axis=0, numeric_only=True).to_dict()}


class DataDescriberSkew(BaseDataDescriber):
    """
    Calculate the skewness of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"skew": data.skew(axis=0, numeric_only=True).to_dict()}


class DataDescriberQ1(BaseDataDescriber):
    """
    Calculate the first quartile of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"q1": data.quantile(0.25, axis=0, numeric_only=True).to_dict()}


class DataDescriberQ3(BaseDataDescriber):
    """
    Calculate the third quartile of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"q3": data.quantile(0.75, axis=0, numeric_only=True).to_dict()}


class DataDescriberIQR(BaseDataDescriber):
    """
    Calculate the interquartile range of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {
            "iqr": (
                data.quantile(0.75, axis=0, numeric_only=True)
                - data.quantile(0.25, axis=0, numeric_only=True)
            ).to_dict()
        }


class DataDescriberRange(BaseDataDescriber):
    """
    Calculate the range of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {
            "range": (
                data.max(axis=0, numeric_only=True)
                - data.min(axis=0, numeric_only=True)
            ).to_dict()
        }


class DataDescriberPercentile(BaseDataDescriber):
    """
    Calculate the k*100 th-percentile of each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _init_config(self, config: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Initialize the configuration parameters.

        Designed to be overridden by subclasses to customize initialization logic.
        """
        if "percentile" not in config:
            error_msg = "percentile not found in config"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)
        if not isinstance(config["percentile"], (int, float)):
            error_msg = "percentile must be a number"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)
        if not 0 <= config["percentile"] <= 1:
            error_msg = "percentile must be between 0 and 1"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)
        return config

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        percentile: int | float = self.config["percentile"]
        return {
            f"{percentile * 100} th " + "percentile": data.quantile(
                percentile, axis=0, numeric_only=True
            ).to_dict()
        }


class DataDescriberColNA(BaseDataDescriber):
    """
    Calculate the number of NA in each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        return {"na_count": data.isna().sum(axis=0).to_dict()}


class DataDescriberNUnique(BaseDataDescriber):
    """
    Calculate the number of unique values in each column in the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        valid_columns: list[str] = []

        for col_name, dtype in data.dtypes.items():
            col = data[col_name]
            if (
                is_bool_dtype(col)
                or is_string_dtype(col)
                or isinstance(dtype, pd.CategoricalDtype)
                or is_object_dtype(col)
            ):
                valid_columns.append(col_name)

        nunique_dict: dict[str, int] = {}
        if valid_columns:
            nunique_dict = data[valid_columns].nunique(axis=0, dropna=True).to_dict()

        return {"nunique": nunique_dict}


class DataDescriberCov(BaseDataDescriber):
    """
    Calculate the covariance matrix of the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        temp = data.cov(numeric_only=True)
        upper_indices = np.triu_indices_from(temp, k=1)
        temp.values[upper_indices] = np.nan

        # 確保索引名稱不會與現有列名衝突
        index_name = "col1"
        if index_name in temp.columns:
            index_name = "index_col1"

        temp = (
            temp.reset_index(names=index_name)
            .melt(
                id_vars=index_name,
                value_vars=temp.columns,
                var_name="col2",
                value_name="cov",
            )
            .dropna()
            .reset_index(drop=True)
        )

        return temp.set_index([index_name, "col2"]).to_dict()


class DataDescriberCorr(BaseDataDescriber):
    """
    Calculate the correlation matrix of the dataset.
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config=config)

    def _eval(self, data: pd.DataFrame) -> dict[str, int | float]:
        temp = data.corr(method="pearson", numeric_only=True)
        upper_indices = np.triu_indices_from(temp, k=1)
        temp.values[upper_indices] = np.nan

        # 確保索引名稱不會與現有列名衝突
        index_name = "col1"
        if index_name in temp.columns:
            index_name = "index_col1"

        temp = (
            temp.reset_index(names=index_name)
            .melt(
                id_vars=index_name,
                value_vars=temp.columns,
                var_name="col2",
                value_name="corr",
            )
            .dropna()
            .reset_index(drop=True)
        )

        return temp.set_index([index_name, "col2"]).to_dict()
