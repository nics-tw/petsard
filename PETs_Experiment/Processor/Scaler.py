import pandas as pd
from PETs_Experiment.Error import UnfittedError
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

class Scaler:
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

    def inverse_transform(self, data):
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        return self._inverse_transform(data)

class Scaler_Standard(Scaler):
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
        Conduct standardisation.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            (np.ndarray): The transformed data.
        """
        
        return self.model.transform(data)
    
    def _inverse_transform(self, data):
        """
        Inverse the transformed data to the data in the original scale.

        Input:
            data (np.ndarray): The data needed to be transformed inversely.

        Output:
            (np.ndarray): The inverse transformed data.
        """
        
        return self.model.inverse_transform(data)

class Scaler_ZeroCenter(Scaler_Standard):
    def __init__(self):
        super().__init__()
        self.model = StandardScaler(with_std=False)

class Scaler_MinMax(Scaler_Standard):
    def __init__(self):
        super().__init__()
        self.model = MinMaxScaler()
