import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

from PETsARD.Error import UnfittedError


class Scaler:
    """
    Base class for all Scaler classes.
    """

    PROC_TYPE = 'scaler'

    def __init__(self) -> None:
        self._is_fitted = False

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data needed to be fitted.
        """
        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        self._fit(data)

        self._is_fitted = True

    def transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `transform`.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        return self._transform(data)

    def inverse_transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `inverse_transform`.

        Args:
            data (pd.Series): The data needed to be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        return self._inverse_transform(data)


class Scaler_Standard(Scaler):
    """
    Apply StandardScaler.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler()

    def _fit(self, data: np.ndarray) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.
        """
        self.model.fit(data)

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct standardisation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        return self.model.transform(data)

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the data in the original scale.

        Args:
            data (np.ndarray): The data needed to be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """

        return self.model.inverse_transform(data)


class Scaler_ZeroCenter(Scaler_Standard):
    """
    Apply StandardScaler without std scaling.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler(with_std=False)


class Scaler_MinMax(Scaler_Standard):
    """
    Apply MinMaxScaler.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model: MinMaxScaler = MinMaxScaler()


class Scaler_Log(Scaler):
    """
    Scale the data by log transformation.
    """

    def __init__(self) -> None:
        super().__init__()

    def _fit(self, data: np.ndarray) -> None:
        """
        Check whether the log transformation can be performed.

        Args:
            data (np.ndarray): The data needed to be transformed.
        """
        if (data <= 0).any():
            raise ValueError(
                'Log transformation does not support non-positive values.')

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct log transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        if (data <= 0).any():
            raise ValueError(
                'Log transformation does not support non-positive values.')
        else:
            return np.log(data)

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the data in the original scale.

        Args:
            data (np.ndarray): The data needed to be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """

        return np.exp(data)
