from abc import ABC, abstractmethod
import itertools
from typing import Union

import pandas as pd
from pandas.api.types import is_numeric_dtype

from PETsARD import Metadata
from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.util import safe_round
from PETsARD.error import ConfigError, UnsupportedMethodError


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
        return self.data['col'].dtype == 'category'

    def _eval(self) -> int:
        """
        Returns:
            (int): The number of unique values in the column.
        """
        return self.data['col'].nunique(dropna=True)


class Stats(EvaluatorBase):
    """
    The "Stats" statistics Evaluator.
        This class is responsible for computing various statistical measures
        on the input data.

    Attr:
        DEFAULT_STATS_METHOD (list):
            A list of default statistics methods to be computed.
        STATS_METHOD (dict):
            A dictionary mapping each statistics method to its corresponding
    """

    DEFAULT_STATS_METHOD: list = ['mean', 'std', 'nunique', 'spearmanr']
    STATS_METHOD: dict[str, dict[str, Union[str, StatsBase]]] = {
        'mean': {
            'infer_dtype': ['numerical'],
            'granularity': 'columnwise',
            'module': StatsMean,
        },
        'std': {
            'infer_dtype': ['numerical'],
            'granularity': 'columnwise',
            'module': StatsStd,
        },
        'nunique': {
            'infer_dtype': ['categorical'],
            'granularity': 'columnwise',
            'module': StatsNUnique,
        },
        'spearmanr': {
            'infer_dtype': ['categorical'],
            'granularity': 'pairwise',
            'module': None,
        },
    }

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration for the statistics evaluation.

        Attr.
            columns_info (dict):
                A dictionary containing information
                about the columns in the input data.
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
        config['stats_method'] = self.DEFAULT_STATS_METHOD
        self.columns_info: dict = {}
        self.result['global'] = None
        self.result['columnwise'] = None
        self.result['pairwise'] = None

    def create(self, data: dict) -> None:
        """
        Args:
            data (dict): The input data dictionary containing 'ori' and 'syn' data.

        Raises:
            ConfigError:
                If 'ori' or 'syn' data is missing in the input data dictionary.
            UnsupportedMethodError:
                If an unsupported statistics method is encountered.
        """
        if not all(key in data for key in ['ori', 'syn']):
            raise ConfigError
        self.data = data
        self.columns_info = self._create_columns_info()

        config_method: dict = None
        infer_dtype: str = None
        granularity: str = None
        module: StatsBase = None
        col_result: dict = {}
        pair_result: dict = {}
        for method in self.config['stats_method']:
            config_method = self.STATS_METHOD[method]
            infer_dtype, granularity, module = (
                config_method['infer_dtype'],
                config_method['granularity'],
                config_method['module'],
            )

            if granularity == 'columnwise':
                for col, value in self.columns_info.items():
                    # Check if the column's data type matches the inferred data type
                    # and the inferred data type is in the list of supported data types
                    if value['infer_dtype_match'] \
                            and value['ori_infer_dtype'] in infer_dtype:
                        col_result = self._create_columnwise_method(
                            col_result, col, method, "ori", module
                        )
                        col_result = self._create_columnwise_method(
                            col_result, col, method, "syn", module
                        )
            elif granularity == 'pairwise':
                for (col1, value1), (col2, value2) in \
                        itertools.combinations(self.columns_info.items(), 2):

                    if value1['ori_infer_dtype'] in infer_dtype \
                            or value2['ori_infer_dtype'] in infer_dtype:
                        pair_result = self._create_pairwise_method(
                            pair_result, col1, col2, method, "ori", module
                        )

                    if value1['syn_infer_dtype'] in infer_dtype \
                            or value2['syn_infer_dtype'] in infer_dtype:
                        pair_result = self._create_pairwise_method(
                            pair_result, col1, col2, method, "syn", module
                        )
            else:
                raise UnsupportedMethodError

        if col_result != {}:
            self.columns_result = pd.DataFrame.from_dict(
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
    def _extract_columns_info(data_type: str, col: pd.Series) -> dict:
        """
        Extracts the columns information.

        Args:
            data_type (str): The type of data ('ori' or 'syn').
            col (pd.Series): The column data.

        Returns:
            (dict): The dictionary containing the extracted column information.
        """
        temp: dict = {}
        dtype: type = col.dtype
        temp['dtype'] = (pd.CategoricalDtype
                         if isinstance(dtype, pd.CategoricalDtype) else dtype)
        temp['infer_dtype'] = Metadata._convert_dtypes(dtype)

        temp = {f"{data_type}_{key}": value for key, value in temp.items()}
        return temp

    def _create_columnwise_method(
        self,
        col_result: dict,
        col: str,
        method: str,
        data_type: str,
        module: StatsBase
    ) -> dict:
        """
        Creates the column-wise method for a specific column.

        Args:
            col_result (dict): The dictionary containing the computed statistics.
            col (str): The column name.
            method (str): The statistics method.
            data_type (str): The type of data ('ori' or 'syn').
            module (StatsBase): The statistics module.

        Returns:
            col_result (dict): The dictionary containing the computed statistics.
        """
        if col not in col_result:
            col_result[col] = {}
        method_data_type: str = f"{method}_{data_type}"

        temp_module: StatsBase = module()
        temp_module.create({'col': self.data[data_type][col]})

        col_result[col][method_data_type] = temp_module.eval()
        return col_result

    def _create_pairwise_method(
        self,
        pair_result: dict,
        col1: str,
        col2: str,
        method: str,
        data_type: str,
        module: StatsBase,
    ) -> dict:
        """
        Creates the pair-wise method for a specific column.

        Args:
            pair_result (dict): The dictionary containing the computed statistics.
            col1 (str): The column 1 name.
            col2 (str): The column 2 name.
            method (str): The statistics method.
            data_type (str): The type of data ('ori' or 'syn').
            module (StatsBase): The statistics module.

        Returns:
            pair_result (dict): The dictionary containing the computed statistics.
        """
        if (col1, col2) not in pair_result:
            pair_result[(col1, col2)] = {
                f"{method}_ori": np.nan,
                f"{method}_syn": np.nan,
            }

        method_data_type: str = f"{method}_{data_type}"

        temp_module: StatsBase = module()
        temp_module.create({
            'col1': self.data[data_type][col1],
            'col2': self.data[data_type][col2],
        })

        pair_result[(col1, col2)][method_data_type] = temp_module.eval()
        return pair_result

    def eval(self):
        """
        Evaluates the computed statistics.
        """
        pass

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
