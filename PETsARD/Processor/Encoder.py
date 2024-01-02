import numpy as np
import pandas as pd
from ..Error import UnfittedError
from sklearn.preprocessing import LabelEncoder

class Encoder:
    def __init__(self) -> None:
        # Mapping dict
        self.cat_to_val = None

        # Labels
        self.labels = None

        self._is_fitted = False

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Input:
            data (pd.Series): The data to be fitted.

        Output:
            None
        """
        self._check_dtype_valid(data)
        self._fit(data)

        self._is_fitted = True

    def transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `transform`.

        Input:
            data (pd.Series): The data to be transformed.

        Output:
            (np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')
        
        self._check_dtype_valid(data)
        
        # Check whether the categories of the column are included in the fitted instance
        if not set(data.unique()).issubset(set(self.labels)):
            raise ValueError("The data contains categories that the object hasn't seen in the fitting process. Please check the data categories again.")
        
        return self._transform(data)

    def inverse_transform(self, data: pd.Series) -> pd.Series | np.ndarray:
        """
        Base method of `inverse_transform`.

        Input:
            data (pd.Series): The data to be inverse transformed.

        Output:
            (pd.Series | np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')
        
        self._check_dtype_valid_inverse(data)
        
        return self._inverse_transform(data)
    
    def _check_dtype_valid(self, data: pd.Series) -> None:
        """
        Check whether the data type is valid.

        Input:
            data (pd.Series): The data to be processed.

        Output:
            None
        """
        if not (pd.api.types.is_object_dtype(data) or isinstance(data.dtypes, pd.CategoricalDtype)):
            raise ValueError(f'The column {data.name} should be in object or categorical format to use an encoder.')
        
    def _check_dtype_valid_inverse(self, data: pd.Series) -> None:
        """
        Check whether the data type is valid for `inverse_transform`.

        Input:
            data (pd.Series): The data to be processed.

        Output:
            None
        """
        if not pd.api.types.is_numeric_dtype(data):
            raise ValueError(f'The column {data.name} should be in numerical format to use inverse_transform method from an encoder.')
    

class Encoder_Uniform(Encoder):
    def __init__(self) -> None:
        super().__init__()
        
        # Lower and upper values
        self.upper_values = None
        self.lower_values = None

        # Initiate a random generator
        self._rgenerator = np.random.default_rng()

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Input:
            data (pd.Series): The categorical data needed to be transformed.

        Output:
            None
        """
        normalize_value_counts = data.value_counts(normalize=True)
        # Get keys (original labels)
        self.labels = normalize_value_counts.index.get_level_values(0).to_list()
        # Get values (upper and lower bounds)
        self.upper_values = np.cumsum(normalize_value_counts.values)
        self.lower_values = np.roll(self.upper_values, 1)
        # To make sure the range of the data is in [0, 1]. That is, the range of an uniform dist.
        self.upper_values[-1] = 1.0
        self.lower_values[0] = 0.0

        self.cat_to_val = dict(zip(self.labels, list(zip(self.lower_values, self.upper_values))))

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a uniform distribution. For example, a column with two categories (e.g., 'Male', 'Female') can be mapped to [0.0, 0.5) and [0.5, 1], respectively.

        Input:
            data (pd.Series): The categorical data needed to be transformed.

        Output:
            (np.ndarray): The transformed data.
        """
        
        if isinstance(data.dtype, pd.api.types.CategoricalDtype):
            data_obj = data.astype(object)
        else:
            data_obj = data.copy()
        
        return data_obj.map(lambda x: self._rgenerator.uniform(self.cat_to_val[x][0], self.cat_to_val[x][1], size=1)[0]).values
    
    def _inverse_transform(self, data: pd.Series) -> pd.Series:
        """
        Inverse the transformed data to the categorical data.

        Input:
            data (pd.Series): The categorical data needed to be transformed inversely.

        Output:
            (pd.Series): The inverse transformed data.
        """
        
        # Check the range of the data is valid
        if data.max() > 1 or data.min() < 0:
            raise ValueError("The range of the data is out of range. Please check the data again.")
        
        bins_val = np.append(self.lower_values, 1.0)
        
        return pd.cut(data, right=False, include_lowest=True, bins=bins_val, labels=self.labels, ordered=False)
        

class Encoder_Label(Encoder):
    def __init__(self) -> None:
        super().__init__()
        self.model = LabelEncoder()

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Input:
            data (pd.Series): The categorical data needed to be transformed.

        Output:
            None
        """
        self.model.fit(data)

        # Get keys (original labels)
        self.labels = list(self.model.classes_)

        self.cat_to_val = dict(zip(self.labels, list(self.model.transform(self.model.classes_))))

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a series of integer labels.

        Input:
            data (pd.Series): The categorical data needed to be transformed.

        Output:
            (np.ndarray): The transformed data.
        """
        
        return self.model.transform(data)
    
    def _inverse_transform(self, data: pd.Series) -> np.ndarray:
        """
        Inverse the transformed data to the categorical data.

        Input:
            data (pd.Series): The categorical data needed to be transformed inversely.

        Output:
            (np.ndarray): The inverse transformed data.
        """
        
        return self.model.inverse_transform(data)
        
        
