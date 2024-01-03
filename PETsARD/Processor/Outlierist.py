import numpy as np
import pandas as pd
from ..Error import UnfittedError
from sklearn.preprocessing import StandardScaler


class Outlierist:
    def __init__(self) -> None:
        self._is_fitted = False
        self.data_backup = None  # for restoring data

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data needed to be fitted.

        Return:
            None
        """
        if not self.IS_GLOBAL_TRANSFORMATION:
            self._check_dtype_valid(data)

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
            (np.ndarray): The filter marking the outliers.
        """
        if not self.IS_GLOBAL_TRANSFORMATION:
            self._check_dtype_valid(data)

        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        return self._transform(data)

    def _check_dtype_valid(self, data: pd.Series) -> None:
        """
        Check whether the data type is valid. Only called by the outlierists conducting local transformation, e.g., Outlierist_ZScore and Outlierist_IQR. The methods for global outlierists are conducted in Mediators.

        Args:
            data (pd.Series): The data to be processed.

        Return:
            None
        """
        if not pd.api.types.is_numeric_dtype(data):
            raise ValueError(
                f'The column {data.name} should be in numerical format to use an outlierist.')


class Outlierist_ZScore(Outlierist):
    # indicator of whether the fit and transform process involved other columns
    IS_GLOBAL_TRANSFORMATION = False

    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler()

    def _fit(self, data: np.ndarray) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            None
        """
        self.model.fit(data)

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct standardisation and mark inliers as 1.0 and outliers as -1.0.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The filter marking the outliers.
        """
        self.data_backup = data

        ss_data = self.model.transform(data)

        return (np.abs(ss_data) > 3).ravel()


class Outlierist_IQR(Outlierist):
    # indicator of whether the fit and transform process involved other columns
    IS_GLOBAL_TRANSFORMATION = False

    def __init__(self) -> None:
        super().__init__()
        self.Q1 = None
        self.Q3 = None
        self.IQR = None
        self.lower = None
        self.upper = None

    def _fit(self, data: np.ndarray) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            None
        """
        self.Q1 = np.quantile(data, 0.25)
        self.Q3 = np.quantile(data, 0.75)
        self.IQR = self.Q3 - self.Q1
        self.lower = self.Q1 - 1.5 * self.IQR
        self.upper = self.Q3 + 1.5 * self.IQR

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct standardisation and mark inliers as 1.0 and outliers as -1.0.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The filter marking the outliers.
        """
        self.data_backup = data

        return (np.logical_or(data > self.upper, data < self.lower)).ravel()


class Outlierist_IsolationForest(Outlierist):
    """
    Dummy class, doing nothing related to the method. 
    It's implemented in the mediator because it's global transformation.
    """
    # indicator of whether the fit and transform process involved other columns
    IS_GLOBAL_TRANSFORMATION = True

    def __init__(self) -> None:
        super().__init__()

    def _fit(self, data: None) -> None:
        pass

    def _transform(self, data: np.ndarray) -> np.ndarray:
        return data.ravel()


class Outlierist_LOF(Outlierist):
    """
    Dummy class, doing nothing related to the method. 
    It's implemented in the mediator because it's global transformation.
    """
    # indicator of whether the fit and transform process involved other columns
    IS_GLOBAL_TRANSFORMATION = True

    def __init__(self) -> None:
        super().__init__()

    def _fit(self, data: None) -> None:
        pass

    def _transform(self, data: np.ndarray) -> np.ndarray:
        return data.ravel()
