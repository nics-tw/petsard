import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from petsard.exceptions import UnfittedError


class OutlierHandler:
    """
    Base class for all OutlierHandler classes.
    """

    PROC_TYPE = ("outlier",)

    def __init__(self) -> None:
        self._is_fitted = False
        self.data_backup = None  # for restoring data

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data needed to be fitted.
        """
        if isinstance(data, pd.Series):
            data = data.values.reshape(-1, 1)

        self._fit(data)

        self._is_fitted = True

    def _fit():
        """
        _fit method is implemented in subclasses.

        fit method is responsible for general action defined by the base class.
        _fit method is for specific procedure conducted by each subclasses.
        """
        raise NotImplementedError(
            "_fit method should be implemented " + "in subclasses."
        )

    def transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `transform`.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (np.ndarray): The filter marking the outliers.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if isinstance(data, pd.Series):
            data = data.values.reshape(-1, 1)

        return self._transform(data)

    def _transform():
        """
        _transform method is implemented in subclasses.

        transform method is responsible for general action
            defined by the base class.
        _transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_transform method should be implemented " + "in subclasses."
        )


class OutlierZScore(OutlierHandler):
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

        # back up the data before transformation
        self.data_backup = data

        ss_data = self.model.transform(data)

        return (np.abs(ss_data) > 3).ravel()


class OutlierIQR(OutlierHandler):
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

        # back up the data before transformation
        self.data_backup = data

        return (np.logical_or(data > self.upper, data < self.lower)).ravel()


class OutlierIsolationForest(OutlierHandler):
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


class OutlierLOF(OutlierHandler):
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
