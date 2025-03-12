import numpy as np
import pandas as pd

from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import ConfigError
from petsard.util import safe_round


class Describer(BaseEvaluator):
    """
    Interface class for Describers.

    Describers are classes that describe the data in the chosen ways.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data.
            - describe (list): A list of methods to describe the data.
            If the method requires a parameter, it should be a dictionary
            with the method name as the key and the parameter as the value.
    """

    def __init__(self, config: dict):
        if "method" not in config:
            raise ConfigError

        self.config: dict = config
        self.data: dict = {}

        self.agg = None

    def _create(self, data):
        """
        Create the worker and send the data to the worker.

        Args:
            data (dict): The data to be described. The key should be 'data',
            and the value should be a pandas DataFrame.
        """
        if not set(["data"]).issubset(set(data.keys())):
            raise ConfigError
        data = {key: value for key, value in data.items() if key == "data"}
        self.data = data
        self.agg = DescriberAggregator(self.config)
        self.agg.create(self.data["data"])

    def eval(self):
        """
        Evaluate the data with the method given in the config.
        """
        self.agg.eval()

    def get_global(self):
        """
        Get the global result of the description/evaluation.
        """
        return self.agg.get_global()

    def get_columnwise(self):
        """
        Get the column-wise result of the description/evaluation.
        """
        return self.agg.get_columnwise()

    def get_pairwise(self):
        """
        Get the pair-wise result of the description/evaluation.
        """
        return self.agg.get_pairwise()


class DescriberBase:
    """
    Base class for describers.
    """

    def __init__(self):
        self.data = None
        self.result = {"global": {}, "columnwise": {}, "pairwise": {}}

    def create(self, data):
        """
        Store the data in the describer.

        Args:
            data (pd.DataFrame): The data to be described.
        """
        self.data = data

    def eval(self):
        raise NotImplementedError("eval method not implemented in DescriberBase")

    def get_global(self):
        return pd.DataFrame(self.result.get("global", {}), index=[0])

    def get_columnwise(self):
        return pd.DataFrame(self.result.get("columnwise", {}))

    def get_pairwise(self):
        return pd.DataFrame(self.result.get("pairwise", {}))


class DescriberRowCount(DescriberBase):
    """
    Calculate the number of rows in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["global"] = {"row_count": int(self.data.shape[0])}


class DescriberColumnCount(DescriberBase):
    """
    Calculate the number of columns in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["global"] = {"col_count": int(self.data.shape[1])}


class DescriberGlobalNA(DescriberBase):
    """
    Calculate the number of rows with NA in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["global"] = {"na_count": int(self.data.isna().any(axis=1).sum())}


class DescriberMean(DescriberBase):
    """
    Calculate the mean of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "mean": self.data.mean(axis=0, numeric_only=True).to_dict()
        }


class DescriberMedian(DescriberBase):
    """
    Calculate the median of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "median": self.data.median(axis=0, numeric_only=True).to_dict()
        }


class DescriberStd(DescriberBase):
    """
    Calculate the standard deviation of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "std": self.data.std(axis=0, numeric_only=True).to_dict()
        }


class DescriberVar(DescriberBase):
    """
    Calculate the variance of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "var": self.data.var(axis=0, numeric_only=True).to_dict()
        }


class DescriberMin(DescriberBase):
    """
    Calculate the minimum of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "min": self.data.min(axis=0, numeric_only=True).to_dict()
        }


class DescriberMax(DescriberBase):
    """
    Calculate the maximum of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "max": self.data.max(axis=0, numeric_only=True).to_dict()
        }


class DescriberKurtosis(DescriberBase):
    """
    Calculate the kurtosis of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "kurtosis": self.data.kurt(axis=0, numeric_only=True).to_dict()
        }


class DescriberSkew(DescriberBase):
    """
    Calculate the skewness of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "skew": self.data.skew(axis=0, numeric_only=True).to_dict()
        }


class DescriberQ1(DescriberBase):
    """
    Calculate the first quartile of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "q1": self.data.quantile(0.25, axis=0, numeric_only=True).to_dict()
        }


class DescriberQ3(DescriberBase):
    """
    Calculate the third quartile of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "q3": self.data.quantile(0.75, axis=0, numeric_only=True).to_dict()
        }


class DescriberIQR(DescriberBase):
    """
    Calculate the interquartile range of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "iqr": (
                self.data.quantile(0.75, axis=0, numeric_only=True)
                - self.data.quantile(0.25, axis=0, numeric_only=True)
            ).to_dict()
        }


class DescriberRange(DescriberBase):
    """
    Calculate the range of each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "range": (
                self.data.max(axis=0, numeric_only=True)
                - self.data.min(axis=0, numeric_only=True)
            ).to_dict()
        }


class DescriberPercentile(DescriberBase):
    """
    Calculate the k*100 th-percentile of each column in the dataset.
    """

    def __init__(self, k):
        super().__init__()
        self.percentile = k

    def eval(self):
        self.result["columnwise"] = {
            f"{self.percentile * 100} th " + "percentile": self.data.quantile(
                self.percentile, axis=0, numeric_only=True
            ).to_dict()
        }


class DescriberColNA(DescriberBase):
    """
    Calculate the number of NA in each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {"na_count": self.data.isna().sum(axis=0).to_dict()}


class DescriberNUnique(DescriberBase):
    """
    Calculate the number of unique values in each column in the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        self.result["columnwise"] = {
            "nunique": self.data.filter(
                self.data.columns[self.data.dtypes == "category"]
            )
            .nunique(axis=0)
            .to_dict()
        }


class DescriberCov(DescriberBase):
    """
    Calculate the covariance matrix of the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        temp = self.data.cov(numeric_only=True)
        upper_indices = np.triu_indices_from(temp, k=1)
        temp.values[upper_indices] = np.nan

        temp = (
            temp.reset_index(names="col1")
            .melt(
                id_vars="col1",
                value_vars=temp.columns,
                var_name="col2",
                value_name="cov",
            )
            .dropna()
            .reset_index(drop=True)
        )

        self.result["pairwise"] = temp.set_index(["col1", "col2"]).to_dict()


class DescriberCorr(DescriberBase):
    """
    Calculate the correlation matrix of the dataset.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def eval(self):
        temp = self.data.corr(method="pearson", numeric_only=True)
        upper_indices = np.triu_indices_from(temp, k=1)
        temp.values[upper_indices] = np.nan

        temp = (
            temp.reset_index(names="col1")
            .melt(
                id_vars="col1",
                value_vars=temp.columns,
                var_name="col2",
                value_name="corr",
            )
            .dropna()
            .reset_index(drop=True)
        )

        self.result["pairwise"] = temp.set_index(["col1", "col2"]).to_dict()


class DescriberAggregator(Describer):
    """
    Aggregates the results of multiple Describers. The worker of Describer.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data.
            - describe (list): A list of methods to describe the data.
            If the method requires a parameter, it should be a dictionary
            with the method name as the key and the parameter as the value.
    """

    _DESCRIBER_MAP = {
        "row_count": ("global", DescriberRowCount),
        "col_count": ("global", DescriberColumnCount),
        "global_na_count": ("global", DescriberGlobalNA),
        "mean": ("columnwise", DescriberMean),
        "median": ("columnwise", DescriberMedian),
        "std": ("columnwise", DescriberStd),
        "var": ("columnwise", DescriberVar),
        "min": ("columnwise", DescriberMin),
        "max": ("columnwise", DescriberMax),
        "kurtosis": ("columnwise", DescriberKurtosis),
        "skew": ("columnwise", DescriberSkew),
        "q1": ("columnwise", DescriberQ1),
        "q3": ("columnwise", DescriberQ3),
        "iqr": ("columnwise", DescriberIQR),
        "range": ("columnwise", DescriberRange),
        "percentile": ("columnwise", DescriberPercentile),
        "col_na_count": ("columnwise", DescriberColNA),
        "nunique": ("columnwise", DescriberNUnique),
        "cov": ("pairwise", DescriberCov),
        "corr": ("pairwise", DescriberCorr),
    }

    _INT_DESCRIBER = ["col_na_count", "nunique"]

    def __init__(self, config: dict):
        super().__init__(config=config)

        self.global_description = []
        self.column_description = []
        self.pairwise_description = []

        self.data_content: pd.DataFrame = None

    def create(self, data):
        """
        Store the data in the aggregator.

        Args:
            data (pd.DataFrame): The data to be described.
        """
        self.data_content = data

    def eval(self):
        """
        Aggregates the results of multiple Describers.

        It aggregates the results of multiple Describers and
        stores the result in self.result.
        """
        # if self.config['method'] is 'default', generate selected describers
        if self.config["method"] == "default":
            self.config["describe"] = [
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

        for met in self.config["describe"]:
            if type(met) is not str:
                # it should be a dict: key is the method,
                # and value is a single parameter
                param = list(met.values())[0]
                met = list(met.keys())[0]

                describer = self._DESCRIBER_MAP[met][1](param)
            else:
                describer = self._DESCRIBER_MAP[met][1]()

            describer.create(self.data_content)
            describer.eval()

            if self._DESCRIBER_MAP[met][0] == "global":
                self.global_description.append(describer)
            elif self._DESCRIBER_MAP[met][0] == "columnwise":
                self.column_description.append(describer)
            elif self._DESCRIBER_MAP[met][0] == "pairwise":
                self.pairwise_description.append(describer)

    def get_global(self) -> pd.DataFrame:
        """
        Get the global result of the description/evaluation.
            Only one row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The global result of the description/evaluation.
        """
        return pd.concat([d.get_global() for d in self.global_description], axis=1)

    def get_columnwise(self) -> pd.DataFrame:
        """
        Get the column-wise result of the description/evaluation.
            Each column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The column-wise result of the description/evaluation.
        """
        c_table = pd.concat(
            [d.get_columnwise() for d in self.column_description], axis=1
        )

        for col in c_table.columns:
            if col in self._INT_DESCRIBER:
                c_table[col] = c_table[col].fillna(-1).astype(int).replace(-1, pd.NA)
            else:
                c_table[col] = safe_round(c_table[col]).fillna(pd.NA)

        return c_table

    def get_pairwise(self) -> pd.DataFrame:
        """
        Get the pair-wise result of the description/evaluation.
            Each column x column is a row, and every property/metrics is columns.

        Returns:
            (pd.DataFrame): The pairwise result of the description/evaluation.
        """
        p_table = pd.concat(
            [d.get_pairwise() for d in self.pairwise_description], axis=1
        )

        for col in p_table.columns:
            p_table[col] = safe_round(p_table[col]).fillna(pd.NA)

        return p_table
