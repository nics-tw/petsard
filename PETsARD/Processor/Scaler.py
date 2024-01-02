import numpy as np
import pandas as pd
from torch import Value
from ..Error import UnfittedError
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

class Scaler:
    def __init__(self) -> None:
        self._is_fitted = False

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Input:
            data (pd.Series): The data needed to be fitted.

        Output:
            None
        """
        self._check_dtype_valid(data)

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        self._fit(data)

        self._is_fitted = True

    def transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `transform`.

        Input:
            data (pd.Series): The data needed to be transformed.

        Output:
            (np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')
        
        self._check_dtype_valid(data)

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        return self._transform(data)

    def inverse_transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `inverse_transform`.

        Input:
            data (pd.Series): The data needed to be transformed inversely.

        Output:
            (np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')
        
        self._check_dtype_valid(data)

        if type(data) == pd.Series:
            data = data.values.reshape(-1, 1)

        return self._inverse_transform(data)
    
    def _check_dtype_valid(self, data: pd.Series) -> None:
        """
        Check whether the data type is valid.

        Input:
            data (pd.Series): The data to be processed.

        Output:
            None
        """
        if not pd.api.types.is_numeric_dtype(data):
            raise ValueError(f'The column {data.name} should be in numerical format to use a scaler.')
    

class Scaler_Standard(Scaler):
    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler()

    def _fit(self, data: np.ndarray) -> None:
        """
        Gather information for transformation and reverse transformation.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            None
        """
        self.model.fit(data)

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct standardisation.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            (np.ndarray): The transformed data.
        """
        
        return self.model.transform(data)
    
    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the data in the original scale.

        Input:
            data (np.ndarray): The data needed to be transformed inversely.

        Output:
            (np.ndarray): The inverse transformed data.
        """
        
        return self.model.inverse_transform(data)

class Scaler_ZeroCenter(Scaler_Standard):
    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler(with_std=False)

class Scaler_MinMax(Scaler_Standard):
    def __init__(self) -> None:
        super().__init__()
        self.model = MinMaxScaler()

class Scaler_Log(Scaler):
    def __init__(self) -> None:
        super().__init__()

    def _fit(self, data: np.ndarray) -> None:
        """
        Check whether the log transformation can be performed.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            None
        """
        if (data <= 0).any():
            raise ValueError('Log transformation does not support non-positive values.')

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct log transformation.

        Input:
            data (np.ndarray): The data needed to be transformed.

        Output:
            (np.ndarray): The transformed data.
        """
        if (data <= 0).any():
            raise ValueError('Log transformation does not support non-positive values.')
        else:
            return np.log(data)
    
    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the data in the original scale.

        Input:
            data (np.ndarray): The data needed to be transformed inversely.

        Output:
            (np.ndarray): The inverse transformed data.
        """
        
        return np.exp(data)
