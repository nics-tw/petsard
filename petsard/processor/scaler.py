import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from petsard.error import UnfittedError


class Scaler:
    """
    Base class for all Scaler classes.
    """

    PROC_TYPE = ("scaler",)

    def __init__(self) -> None:
        self._is_fitted = False

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
            (np.ndarray): The transformed data.
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
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if isinstance(data, pd.Series):
            data = data.values.reshape(-1, 1)

        return self._inverse_transform(data)

    def _inverse_transform():
        """
        _inverse_transform method is implemented in subclasses.

        inverse_transform method is responsible for general action
            defined by the base class.
        _inverse_transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_inverse_transform method should be " + "implemented in subclasses."
        )


class ScalerStandard(Scaler):
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


class ScalerZeroCenter(ScalerStandard):
    """
    Apply StandardScaler without std scaling.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler(with_std=False)


class ScalerMinMax(ScalerStandard):
    """
    Apply MinMaxScaler.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model: MinMaxScaler = MinMaxScaler()


class ScalerLog(Scaler):
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
            raise ValueError("Log transformation does not support non-positive values.")

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct log transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        if (data <= 0).any():
            raise ValueError("Log transformation does not support non-positive values.")
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


class ScalerTimeAnchor(Scaler):
    """
    Transform datetime columns into relative time differences.
    By default, it will automatically choose a reference time:
    1. If there's another datetime column not using ScalerTimeAnchor, use the first one as reference
    2. Otherwise, use the earliest timestamp from all datetime columns as reference
    """

    def __init__(self, unit: str = "D") -> None:
        """
        Args:
            unit: Unit for conversion, 'D' for days or 'S' for seconds
        """
        super().__init__()
        if unit not in ["D", "S"]:
            raise ValueError("unit must be either 'D'(days) or 'S'(seconds)")
        self.unit = unit
        self.reference_time = None

    def set_reference_time(self, reference_time: pd.Timestamp) -> None:
        """Set reference timestamp"""
        self.reference_time = reference_time

    def _fit(self, data: np.ndarray) -> None:
        """Validate data type and set reference time if not set"""
        if not pd.api.types.is_datetime64_any_dtype(data):
            raise ValueError("Data must be in datetime format")

        # If reference time is not set, use the earliest timestamp in this column
        if self.reference_time is None:
            self.reference_time = pd.Series(data.ravel()).min()

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """Transform to time differences"""
        if self.reference_time is None:
            raise ValueError("Reference time not set")

        delta = pd.Series(data.ravel()) - self.reference_time

        if self.unit == "D":
            return (delta.dt.total_seconds() / (24 * 3600)).values.reshape(-1, 1)
        else:
            return delta.dt.total_seconds().values.reshape(-1, 1)

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """Restore to original datetime"""
        if self.reference_time is None:
            raise ValueError("Reference time not set")

        if self.unit == "D":
            delta = pd.Series(data.ravel()) * pd.Timedelta(days=1)
        else:
            delta = pd.Series(data.ravel()) * pd.Timedelta(seconds=1)

        return (self.reference_time + delta).values.reshape(-1, 1)
