import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer

from petsard.exceptions import UnfittedError


class DiscretizingHandler:
    """
    Base class for all Discretizer.
    """

    PROC_TYPE = ("discretizing",)

    def __init__(self) -> None:
        self._is_fitted = False

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data to be fitted.
        """
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
            data (pd.Series): The data to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

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
            data (pd.Series): The data to be inverse transformed.

        Return:
            (np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

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

    def _drop_na(self, data: pd.Series) -> pd.Series:
        """
        Drop NA values in the data.
            Workaround for PAC-Synth or simliar synthesizers.
            See issue #440.

        Args:
            data (pd.Series): The data to be processed.

        Return:
            (pd.Series): The data without NA values.
        """
        if data.isna().any():
            return data.copy().dropna()
        else:
            return data


class DiscretizingKBins(DiscretizingHandler):
    """
    Implement a K-bins discretizing method.
    """

    def __init__(self, n_bins: int = 5) -> None:
        """
        Args:
            n_bins (int, default=5): The number of bins.
        """
        super().__init__()
        self.model = KBinsDiscretizer(
            encode="ordinal", strategy="uniform", n_bins=n_bins, subsample=200000
        )
        self.bin_edges: np.ndarray = None
        self.is_constant = False  # Flag for constant data

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.
        Redundant for KBinsDiscretizer.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Fit and transform numerical data to a series of integer labels.

        Args:
            data (pd.Series): The numerical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        if len(data.unique()) < 2:
            warnings.warn(
                f"{data.name} is constant." + " No transformation will be applied."
            )
            self.is_constant = True
            return data.values

        self.model.fit(data.values.reshape(-1, 1))

        self.bin_edges = self.model.bin_edges_

        return self.model.transform(data.values.reshape(-1, 1)).ravel()

    def _inverse_transform(self, data: pd.Series) -> np.ndarray:
        """
        Inverse the transformed data to the numerical data.

        Args:
            data (pd.Series): The categorical data needed to
            be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """
        data = self._drop_na(data)

        if self.is_constant:
            return data.values

        return self.model.inverse_transform(data.values.reshape(-1, 1)).ravel()
