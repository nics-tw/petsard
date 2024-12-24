from abc import ABC, abstractmethod
import itertools
from typing import Union
import warnings

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from scipy.spatial.distance import jensenshannon

from PETsARD import Metadata
from PETsARD.error import ConfigError, UnsupportedMethodError
from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.util import safe_round


class StatsBase(ABC):
    """
    Base class for statistics evaluation.
    """

    def __init__(self):
        """
        Attr:
            data (dict[str, pd.Series]): The data to be evaluated.
        """
        self.data: dict[str, pd.Series] = None

    def create(self, data: dict[str, pd.Series]):
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Raises:
            TypeError: If the data type verification fails.
        """
        self.data = data
        if not self._verify_dtype():
            raise TypeError

    @abstractmethod
    def _verify_dtype(self) -> bool:
        """
        Verifies the data type of the statistics.

        Returns:
            (bool): True if the data type verification passes, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def eval(self) -> int | float:
        """
        Evaluates the statistics and returns the result.
            safe_round is used to round 6 digits the result if it is a float.

        Returns:
            (int | float): The result of the statistics evaluation.
        """
        result: int | float = self._eval()
        return safe_round(result) if isinstance(result, float) else result

    @abstractmethod
    def _eval(self) -> int | float:
        """
        Performs the evaluation of the statistics.

        Returns:
            (int | float): The result of the statistics evaluation.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError


class StatsMean(StatsBase):
    """
    A class of column-wise statistic for the mean.
        Inherits from StatsBase.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the column's data type is numeric, False otherwise.
        """
        return is_numeric_dtype(self.data['col'])

    def _eval(self) -> float:
        """
        Returns:
            (float): The mean value of the column.
        """
        return self.data['col'].mean()


class StatsStd(StatsBase):
    """
    A class of column-wise statistic for the standard deviation.
        Inherits from StatsBase.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the column's data type is numeric, False otherwise.
        """
        return is_numeric_dtype(self.data['col'])

    def _eval(self) -> float:
        """
        Returns:
            (float): The standard deviation of the column.
        """
        return self.data['col'].std()


class StatsMedian(StatsBase):
    """
    A class of column-wise statistic for the median.
        Inherits from StatsBase.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the column's data type is numeric, False otherwise.
        """
        return is_numeric_dtype(self.data['col'])

    def _eval(self) -> int | float:
        """
        Returns:
            (int | float): The median of the column.
        """
        return self.data['col'].median()


class StatsMin(StatsBase):
    """
    A class of column-wise statistic for the min.
        Inherits from StatsBase.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the column's data type is numeric, False otherwise.
        """
        return is_numeric_dtype(self.data['col'])

    def _eval(self) -> int | float:
        """
        Returns:
            (int | float): The min of the column.
        """
        return self.data['col'].min()


class StatsMax(StatsBase):
    """
    A class of column-wise statistic for the max.
        Inherits from StatsBase.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the column's data type is numeric, False otherwise.
        """
        return is_numeric_dtype(self.data['col'])

    def _eval(self) -> int | float:
        """
        Returns:
            (int | float): The max of the column.
        """
        return self.data['col'].max()


class StatsNUnique(StatsBase):
    """
    A class of column-wise statistic for the number of unique values.
        Inherits from the StatsBase.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the data type is 'category', False otherwise.
        """
        return isinstance(self.data['col'].dtype, pd.CategoricalDtype) \
            or self.data['col'].dtype == np.dtype('bool')

    def _eval(self) -> int:
        """
        Returns:
            (int): The number of unique values in the column.
        """
        return self.data['col'].nunique(dropna=True)


class StatsJSDivergence(StatsBase):
    """
    A class of pair-wise statistic for the Jensen–Shannon divergence.
        Inherits from the StatsBase.
    """

    def _verify_dtype(self) -> bool:
        """
        Returns:
            (bool): True if the data type is 'category', False otherwise.
        """
        return (isinstance(self.data['col_ori'].dtype, pd.CategoricalDtype)
                and isinstance(self.data['col_syn'].dtype, pd.CategoricalDtype)
                ) or ((self.data['col_ori'].dtype == np.dtype('bool'))
                and (self.data['col_syn'].dtype == np.dtype('bool'))
                )

    def _eval(self) -> int:
        """
        Returns:
            (float): The Jensen-Shannon divergence of column pair.
        """
        value_cnts_ori = self.data['col_ori'].value_counts(normalize=True)
        value_cnts_syn = self.data['col_syn'].value_counts(normalize=True)

        # Get the set of unique categories from both columns
        all_categories = set(value_cnts_ori.index) | set(value_cnts_syn.index)

        # Fill in missing categories with 0 probability
        p = np.array([value_cnts_ori.get(cat, 0) for cat in all_categories])
        q = np.array([value_cnts_syn.get(cat, 0) for cat in all_categories])

        return jensenshannon(p, q) ** 2


class Stats(EvaluatorBase):
    """
    The "Stats" statistics Evaluator.
        This class is responsible for computing various statistical measures
        on the input data.

    Attr:
        STATS_METHODS (dict):
            A dictionary mapping each statistics method to its corresponding
        COMPARE_METHODS (list[str]):
            A list of supported comparison methods.
        AGGREGATED_METHODS (list[str]):
            A list of supported aggregated methods.
        DEFAULT_METHODS (dict):
            A dictionary containing the default statistics methods.
    """
    STATS_METHODS: dict[str, dict[str, Union[str, StatsBase]]] = {
        'mean': {
            'infer_dtype': ['numerical'],
            'exec_granularity': 'columnwise',
            'module': StatsMean,
        },
        'std': {
            'infer_dtype': ['numerical'],
            'exec_granularity': 'columnwise',
            'module': StatsStd,
        },
        'median': {
            'infer_dtype': ['numerical'],
            'exec_granularity': 'columnwise',
            'module': StatsMedian,
        },
        'min': {
            'infer_dtype': ['numerical'],
            'exec_granularity': 'columnwise',
            'module': StatsMin,
        },
        'max': {
            'infer_dtype': ['numerical'],
            'exec_granularity': 'columnwise',
            'module': StatsMax,
        },
        'nunique': {
            'infer_dtype': ['categorical'],
            'exec_granularity': 'columnwise',
            'module': StatsNUnique,
        },
        'jsdivergence': {
            'infer_dtype': ['categorical'],
            'exec_granularity': 'percolumn',
            'module': StatsJSDivergence,
        },
    }
    COMPARE_METHODS: list[str] = ['diff', 'pct_change']
    AGGREGATED_METHODS: list[str] = ['mean']
    SUMMARY_METHODS: list[str] = ['mean']
    DEFAULT_METHODS: dict[str, str] = {
        'stats_method': [
            'mean', 'std', 'median', 'min', 'max',
            'nunique', 'jsdivergence',
        ],
        'compare_method': 'pct_change',
        'aggregated_method': 'mean',
        'summary_method': 'mean'
    }

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration for the statistics evaluation.
                stats_method (list[str], optional):
                    The list of statistics methods to be computed.
                    Default is ['mean', 'std', 'median', 'min', 'max',
                        'nunique', 'jsdivergence',].
                compare_method (str, optional):
                    The method to compare the original and synthetic data.
                    Default is 'pct_change'.
                aggregated_method (str, optional):
                    The method to aggregate the statistics to global levels
                    Default is 'mean'.
                summary_method (str, optional):
                    The method to finally summarize the global statistics
                    Default is 'mean'.

        Attr.
            columns_info (dict):
                A dictionary containing information
                about the columns in the input data.
            aggregated_percolumn_method (list[str]):
                A list of statistics methods that are aggregated per column.
            result  (dict):
                A dictionary to store the result of the statistics evaluation.
                - global (pd.DataFrame | None):
                    The global statistics dataframe or None if not available.
                - columnwise (pd.DataFrame | None):
                    The column-wise statistics dataframe or None if not available.
                - pairwise (pd.DataFrame | None):
                    The pairwise statistics dataframe or None if not available.
        """
        super().__init__(config=config)

        self._init_config_method('stats_method', self.STATS_METHODS)
        self._init_config_method('compare_method', self.COMPARE_METHODS)
        self._init_config_method('aggregated_method', self.AGGREGATED_METHODS)
        self._init_config_method('summary_method', self.SUMMARY_METHODS)

        self.columns_info: dict = {}
        self.aggregated_percolumn_method: list = [
            stats_method for stats_method in self.config['stats_method']
            if self.STATS_METHODS[stats_method]['exec_granularity'] == 'percolumn'
        ]
        self.result['global'] = None
        self.result['columnwise'] = None
        self.result['pairwise'] = None

    def _init_config_method(self, method_name, valid_methods):
        """
        Initializes the configuration method for the given method name.

        Args:
            method_name (str):
                The name of the method to initialize the configuration for.
            valid_methods (list): A list of valid method names.

        Raises:
            UnsupportedMethodError:
                If the configured method is not in the list of valid methods.

        """
        if method_name in self.config:
            if isinstance(self.config[method_name], str):
                self.config[method_name] = [self.config[method_name]]

            if isinstance(self.config[method_name], list):
                new_method_name: list[str] = []

                for name in self.config[method_name]:
                    name = name.lower()
                    if name not in valid_methods:
                        raise UnsupportedMethodError

                    new_method_name.append(name)

                if method_name == 'stats_method':
                    self.config[method_name] = new_method_name
                else:
                    if len(new_method_name) >= 2:
                        warnings.warn(
                            f'{method_name} only accept one method,' +
                            'methods after the first one will be ignored',
                            Warning)
                    self.config[method_name] = new_method_name[0]
            else:
                raise ConfigError
        else:
            self.config[method_name] = self.DEFAULT_METHODS[method_name]

    def _create(self, data: dict) -> None:
        """
        Args:
            data (dict): The input data dictionary containing 'ori' and 'syn' data.

        Raises:
            ConfigError:
                If 'ori' or 'syn' data is missing in the input data dictionary.
            UnsupportedMethodError:
                If an unsupported statistics method is encountered.
        """
        if not set(['ori', 'syn']).issubset(set(data.keys())):
            raise ConfigError
        data = {key: value for key, value in data.items()
                if key in ['ori', 'syn']
        }
        self.data = data
        self.columns_info = self._create_columns_info()

        config_method: dict = None
        infer_dtype: str = None
        exec_granularity: str = None
        module: StatsBase = None
        col_result: dict = {}
        pair_result: dict = {}

        for method in self.config['stats_method']:
            config_method = self.STATS_METHODS[method]
            infer_dtype, exec_granularity, module = (
                config_method['infer_dtype'],
                config_method['exec_granularity'],
                config_method['module'],
            )

            # Check if the column's data type matches the inferred data type
            # and the inferred data type is in the list of supported data types
            if exec_granularity == 'columnwise':
                for col, value in self.columns_info.items():
                    if col not in col_result:
                        col_result[col] = {}
                    if value['infer_dtype_match'] \
                            and value['ori_infer_dtype'] in infer_dtype:
                        col_result = self._create_columnwise_method(
                            col_result, col, method, "ori", module)
                        col_result = self._create_columnwise_method(
                            col_result, col, method, "syn", module)
                    # avoid no infer_dtype match in whole dataset
                    #   e.g. no category column in data
                    else:
                        col_result[col][f'{method}_ori'] = np.nan
                        col_result[col][f'{method}_syn'] = np.nan
            elif exec_granularity == 'percolumn':
                for col, value in self.columns_info.items():
                    if col not in col_result:
                        col_result[col] = {}
                    if value['infer_dtype_match'] \
                            and value['ori_infer_dtype'] in infer_dtype:
                        col_result = self._create_percolumn_method(
                            col_result, col, method, module)
                    else:
                        col_result[col][method] = np.nan
            elif exec_granularity == 'pairwise':
                for (col1, value1), (col2, value2) in \
                        itertools.combinations(self.columns_info.items(), 2):
                    if (col1, col2) not in pair_result:
                        pair_result[(col1, col2)] = {
                            f"{method}_ori": np.nan,
                            f"{method}_syn": np.nan,
                        }
                    if value1['ori_infer_dtype'] in infer_dtype \
                            and value2['ori_infer_dtype'] in infer_dtype:
                        pair_result = self._create_pairwise_method(
                            pair_result, col1, col2, method, "ori", module
                        )

                    if value1['syn_infer_dtype'] in infer_dtype \
                            and value2['syn_infer_dtype'] in infer_dtype:
                        pair_result = self._create_pairwise_method(
                            pair_result, col1, col2, method, "syn", module
                        )
            else:
                raise UnsupportedMethodError

        if col_result != {}:
            self.result['columnwise'] = pd.DataFrame.from_dict(
                col_result, orient='index')
        if pair_result != {}:
            self.result['pairwise'] = pd.DataFrame.from_dict(
                pair_result, orient='index')

    def _create_columns_info(self) -> dict:
        """
        Creates the columns information dictionary.

        Returns:
            columns_info (dict): The dictionary containing information
                about the columns in the input data.
        """
        columns_info: dict = {}
        ori_colnames: list = self.data['ori'].columns
        syn_colnames: list = self.data['syn'].columns
        colnames = list(set(ori_colnames) & set(syn_colnames))

        temp: dict = {}
        for col in colnames:
            if col in ori_colnames:
                temp.update(
                    self._extract_columns_info('ori', self.data['ori'][col]))
            if col in syn_colnames:
                temp.update(
                    self._extract_columns_info('syn', self.data['syn'][col]))
            temp['dtype_match'] = temp['ori_dtype'] == temp['syn_dtype']
            temp['infer_dtype_match'] = (
                temp['ori_infer_dtype'] == temp['syn_infer_dtype'])

            columns_info[col] = temp
            temp = {}
        return columns_info

    @staticmethod
    def _extract_columns_info(data_source: str, col: pd.Series) -> dict:
        """
        Extracts the columns information.

        Args:
            data_source (str): The type of data ('ori' or 'syn').
            col (pd.Series): The column data.

        Returns:
            (dict): The dictionary containing the extracted column information.
        """
        temp: dict = {}
        dtype: type = col.dtype
        temp['dtype'] = dtype
        temp['infer_dtype'] = Metadata._convert_dtypes(dtype)

        temp = {f"{data_source}_{key}": value for key, value in temp.items()}
        return temp

    def _create_columnwise_method(
        self,
        col_result: dict,
        col: str,
        method: str,
        data_source: str,
        module: StatsBase
    ) -> dict:
        """
        Creates the column-wise method for a specific column.

        Args:
            col_result (dict): The dictionary containing the computed statistics.
            col (str): The column name.
            method (str): The statistics method.
            data_source (str): The source of data ('ori' or 'syn').
            module (StatsBase): The statistics module.

        Returns:
            col_result (dict): The dictionary containing the computed statistics.
        """
        method_data_source: str = f"{method}_{data_source}"

        temp_module: StatsBase = module()
        temp_module.create({'col': self.data[data_source][col]})

        col_result[col][method_data_source] = temp_module.eval()
        return col_result

    def _create_percolumn_method(
        self,
        col_result: dict,
        col: str,
        method: str,
        module: StatsBase,
    ) -> dict:
        """
        Creates the per-column method for a specific column.

        Args:
            col_result (dict): The dictionary containing the computed statistics.
            col (str): The column name.
            method (str): The statistics method.
            module (StatsBase): The statistics module.

        Returns:
            col_result (dict): The dictionary containing the computed statistics.
        """
        temp_module: StatsBase = module()
        temp_module.create({
            'col_ori': self.data['ori'][col],
            'col_syn': self.data['syn'][col],
        })

        col_result[col][method] = temp_module.eval()
        return col_result

    def _create_pairwise_method(
        self,
        pair_result: dict,
        col1: str,
        col2: str,
        method: str,
        data_source: str,
        module: StatsBase,
    ) -> dict:
        """
        Creates the pair-wise method for a specific column.

        Args:
            pair_result (dict): The dictionary containing the computed statistics.
            col1 (str): The column 1 name.
            col2 (str): The column 2 name.
            method (str): The statistics method.
            data_source (str): The type of data ('ori' or 'syn').
            module (StatsBase): The statistics module.

        Returns:
            pair_result (dict): The dictionary containing the computed statistics.
        """
        method_data_source: str = f"{method}_{data_source}"

        temp_module: StatsBase = module()
        temp_module.create({
            'col1': self.data[data_source][col1],
            'col2': self.data[data_source][col2],
        })

        pair_result[(col1, col2)][method_data_source] = temp_module.eval()
        return pair_result

    def eval(self):
        """
        Evaluates the computed statistics.
        """
        compare_method: str = self.config['compare_method']
        aggregated_method: str = self.config['aggregated_method']
        summary_method: str = self.config['summary_method']

        compare_col: list[str] = None
        global_result: dict = {}
        for granularity in ['columnwise', 'pairwise']:
            if granularity in self.result \
                    and self.result[granularity] is not None:
                if compare_method == 'diff':
                    self.result[granularity] = self._compare_diff(
                        self.result[granularity])
                elif compare_method == 'pct_change':
                    self.result[granularity] = self._compare_pct_change(
                        self.result[granularity])

                compare_col = [
                    col for col in self.result[granularity]
                    if col.endswith(f'_{compare_method}')]
                compare_col += self.aggregated_percolumn_method
                if aggregated_method == 'mean':
                    global_result.update(
                        self._aggregated_mean(
                            self.result[granularity][compare_col]
                        )
                    )

        if summary_method == 'mean':
            global_result = {
                'Score': self._summary_mean(global_result),
                **global_result
            }

        self.result['global'] = pd.DataFrame.from_dict(
            global_result, orient='index').T

    @staticmethod
    def _compare_diff(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the difference
            between original and synthetic columns in a DataFrame.

        Args:
            df (pd.DataFrame):
                The DataFrame containing the original and synthetic columns.

        Returns:
            (pd.DataFrame): The DataFrame with the percentage change columns added.

        Raises:
            ValueError: If any of the synthetic columns are missing in the DataFrame.
        """
        ori_cols: list[str] = [
            col for col in df.columns if col.endswith('_ori')]
        syn_cols: list[str] = [col.replace('_ori', '_syn') for col in ori_cols]
        if not all(col in df.columns for col in syn_cols):
            raise ValueError

        eval_col: str = ''
        for ori_col, syn_col in zip(ori_cols, syn_cols):
            eval_col = f'{ori_col.replace("_ori", "_diff")}'
            if eval_col in df.columns:
                df.drop(columns=[eval_col], inplace=True)
            df.insert(df.columns.get_loc(syn_col) + 1, eval_col, np.nan)

            df[eval_col] = safe_round(df[syn_col] - df[ori_col])
        return df

    @staticmethod
    def _compare_pct_change(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the absolute percentage change
            between original and synthetic columns in a DataFrame.
            If original value is 0, return np.nan.
            Add the absolute to avoid the situation that
                original value is negative but synthetic value is positive.

        Args:
            df (pd.DataFrame):
                The DataFrame containing the original and synthetic columns.

        Returns:
            (pd.DataFrame): The DataFrame with the percentage change columns added.

        Raises:
            ValueError: If any of the synthetic columns are missing in the DataFrame.
        """
        ori_cols: list[str] = [
            col for col in df.columns if col.endswith('_ori')]
        syn_cols: list[str] = [col.replace('_ori', '_syn') for col in ori_cols]
        if not all(col in df.columns for col in syn_cols):
            raise ValueError

        eval_col: str = ''
        for ori_col, syn_col in zip(ori_cols, syn_cols):
            eval_col = f'{ori_col.replace("_ori", "_pct_change")}'
            if eval_col in df.columns:
                df.drop(columns=[eval_col], inplace=True)
            df.insert(df.columns.get_loc(syn_col) + 1, eval_col, np.nan)

            df[eval_col] = np.where(
                df[ori_col].astype(float) == 0.0,
                np.nan,
                safe_round((df[syn_col] - df[ori_col]) / abs(df[ori_col]))
            )
        return df

    @staticmethod
    def _aggregated_mean(df: pd.DataFrame) -> dict:
        """
        Calculate the aggregated mean of a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to calculate the mean.

        Returns:
            (dict): A dictionary containing
                the column names as keys
                and the aggregated mean values as values.
        """
        return {k: safe_round(v) for k, v
                in df.mean().to_dict().items()
                }

    @staticmethod
    def _summary_mean(global_result: dict) -> float:
        """
        Calculate the mean of the values in the given dictionary.

        Args:
            global_result (dict): A dictionary containing the values.

        Returns:
            (float): The mean of the values in the dictionary.
        """
        return safe_round(np.mean(list(global_result.values())))

    def get_global(self) -> pd.DataFrame | None:
        """
        Returns the global statistics.

        Returns:
            (pd.DataFrame | None):
                The global statistics dataframe or None if not available.
        """
        return self.result['global']

    def get_columnwise(self) -> pd.DataFrame | None:
        """
        Returns the column-wise statistics.

        Returns:
            (pd.DataFrame | None):
                The column-wise statistics dataframe or None if not available.
        """
        return self.result['columnwise']

    def get_pairwise(self) -> pd.DataFrame | None:
        """
        Returns the pairwise statistics.

        Returns:
            (pd.DataFrame | None):
                The pairwise statistics dataframe or None if not available.
        """
        return self.result['pairwise']
