from copy import deepcopy

import numpy as np
import pandas as pd

from ..Error import UnfittedError


class Missingist:
    """
    Base class for all Missingist classes.

    Args:
        None

    Return:
        None
    """
    def __init__(self) -> None:
        self._is_fitted: bool = False
        self.na_percentage: float = None
        self._imputation_index: list = None
        self._imputation_index_len: int = 0
        self.rng = np.random.default_rng()

    def set_na_percentage(self, na_percentage: float = 0.0) -> None:
        """
        Set NA percentage for the instance.

        Args:
            na_percentage (float, default=0.0): NA percentage from the metadata.

        Return:
            None
        """
        if na_percentage > 1.0 or na_percentage < 0.0:
            raise ValueError(
                'Invalid NA percentage. It should be between 0.0 and 1.0.')

        self.na_percentage = na_percentage

    def set_imputation_index(self, index_list: list = []) -> None:
        """
        Determine which indices can be imputed as NA globally.

        Args:
            index_list (float, default=0.0): NA percentage from the metadata.

        Return:
            None
        """
        if type(index_list) != list:
            raise ValueError('Invalid index_list. It should be a list.')

        self._imputation_index = index_list
        self._imputation_index_len = len(index_list)

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data needed to be fitted.

        Return:
            None
        """
        self._fit(data)

        self._is_fitted = True

    def transform(self, data: pd.Series) -> pd.Series | np.ndarray:
        """
        Base method of `transform`.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (pd.Series | np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        return self._transform(data)

    def inverse_transform(self, data: pd.Series) -> pd.Series:
        """
        Insert NA into the data to have the same pattern with the original data.

        Args:
            data (pd.Series): The data needed to be transformed inversely.

        Return:
            (pd.Series): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if self.na_percentage == 0.0 or self._imputation_index_len == 0:
            return data
        else:
            _na_mask = self.rng.choice(self._imputation_index,
                                       size=int(self.na_percentage *
                                                self._imputation_index_len),
                                       replace=False)
            _col_data: pd.Series = deepcopy(data)
            _col_data.iloc[_na_mask] = np.nan

            return _col_data

    def _check_dtype_valid(self, data: pd.Series) -> None:
        """
        Check whether the data type is numerical type. Only called by Missingist_Mean and Missingist_Median.

        Args:
            data (pd.Series): The data to be processed.

        Return:
            None
        """
        if not pd.api.types.is_numeric_dtype(data):
            raise ValueError(
                f'The column {data.name} should be in numerical format to use the current missingist.')


class Missingist_Mean(Missingist):
    """
    Impute NA values with the mean value.

    Args:
        None

    Return:
        None
    """
    def __init__(self) -> None:
        super().__init__()
        self.data_mean: float = None

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            None
        """
        self._check_dtype_valid(data)

        self.data_mean = data.mean()

    def _transform(self, data: pd.Series) -> pd.Series:
        """
        Fill NA with mean.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        self._check_dtype_valid(data)

        return data.fillna(self.data_mean).values.ravel()

    def _inverse_transform(self, data: None) -> None:
        pass  # Redundant


class Missingist_Median(Missingist):
    """
    Impute NA values with the median value.

    Args:
        None

    Return:
        None
    """
    def __init__(self) -> None:
        super().__init__()
        self.data_median: float = None

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            None
        """
        self._check_dtype_valid(data)

        self.data_median = data.median()

    def _transform(self, data: pd.Series) -> pd.Series:
        """
        Fill NA with median.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        self._check_dtype_valid(data)

        return data.fillna(self.data_median).values.ravel()

    def _inverse_transform(self, data: None) -> None:
        pass  # Redundant


class Missingist_Simple(Missingist):
    """
    Impute NA values with the given value.

    Args:
        value (float, default=0.0): The value for imputation.

    Return:
        None
    """
    def __init__(self, value: float = 0.0) -> None:
        super().__init__()
        self.data_value: float = value

    def _fit(self, data: None) -> None:
        pass  # Redundant

    def _transform(self, data: pd.Series) -> pd.Series:
        """
        Fill NA with the predefined value.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        return data.fillna(self.data_value).values.ravel()

    def _inverse_transform(self, data: None) -> None:
        pass  # Redundant


class Missingist_Drop(Missingist):
    """
    Drop the rows with NA values.

    Args:
        None

    Return:
        None
    """
    def __init__(self) -> None:
        super().__init__()
        self.data_backup: pd.Series = None  # for restoring data

    def _fit(self, data: None) -> None:
        pass  # Redundant

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Mark the NA cells and store the original data.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (np.ndarray): The filter marking the NA cells.
        """
        self.data_backup = data

        return data.isna().values.ravel()

    def _inverse_transform(self, data: None) -> None:
        pass  # Redundant
