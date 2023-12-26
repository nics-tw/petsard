import numpy as np
import pandas as pd
from PETs_Experiment.Error import UnfittedError
from sklearn.preprocessing import StandardScaler

class Outlierist:
    def __init__(self):
        self._is_fitted = False

    def fit(self, data):
        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        self._fit(data)

        self._is_fitted = True

    def transform(self, data):
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        return self._transform(data)

class Outlierist_ZScore(Outlierist):
    def __init__(self):
        super().__init__()
        self.model = StandardScaler()

    def _fit(self, data):
        """
        Gather information for transformation and reverse transformation.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            None
        """
        self.model.fit(data)

    def _transform(self, data):
        """
        Conduct standardisation and mark inliers as 1.0 and outliers as -1.0.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            (np.ndarray): The filter marking the outliers.
        """
        
        ss_data = self.model.transform(data)

        return np.abs(ss_data) > 3

class Outlierist_IQR(Outlierist):
    def __init__(self):
        super().__init__()
        self.Q1 = None
        self.Q3 = None
        self.IQR = None
        self.lower = None
        self.upper = None

    def _fit(self, data):
        """
        Gather information for transformation and reverse transformation.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            None
        """
        self.Q1 = np.quantile(data, 0.25)
        self.Q3 = np.quantile(data, 0.75)
        self.IQR = self.Q3 - self.Q1
        self.lower = self.Q1 - 1.5 * self.IQR
        self.upper = self.Q3 + 1.5 * self.IQR

    def _transform(self, data):
        """
        Conduct standardisation and mark inliers as 1.0 and outliers as -1.0.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            (np.ndarray): The filter marking the outliers.
        """

        return np.logical_or(data > self.upper, data < self.lower)
