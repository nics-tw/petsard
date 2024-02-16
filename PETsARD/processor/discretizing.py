import numpy as np
import pandas as pd

from sklearn.preprocessing import KBinsDiscretizer

from PETsARD.error import UnfittedError

class DiscretizingHandler:
    """
    Base class for all Discretizer.
    """

    PROC_TYPE = ('discretizing',)

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
            raise UnfittedError('The object is not fitted. Use .fit() first.')
        
        return self._transform(data)
    
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
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        return self._inverse_transform(data)
    
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
        self.model = KBinsDiscretizer(encode='ordinal', 
                                      strategy='uniform', 
                                      n_bins=n_bins,
                                      subsample=200000)
        self.bin_edges: np.ndarray = None

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        if len(data.unique()) < 2:
            raise ValueError(f'{data.name} is constant.' + \
                             ' Please drop the data or change the data type' +\
                             ' to categorical.')
        self.model.fit(data.values.reshape(-1, 1))

        self.bin_edges = self.model.bin_edges_

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform numerical data to a series of integer labels.

        Args:
            data (pd.Series): The numerical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

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

        return self.model.inverse_transform(data.values.reshape(-1, 1)).ravel()