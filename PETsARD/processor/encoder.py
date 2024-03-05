import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from PETsARD.error import UnfittedError


class Encoder:
    """
    Base class for all Encoder classes.
    """

    PROC_TYPE = ('encoder',)

    def __init__(self) -> None:
        # Mapping dict
        self.cat_to_val = None

        # Labels
        self.labels = None

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
        raise NotImplementedError("_fit method should be implemented " + \
                                  "in subclasses.")

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

        # Check whether the categories of the column are 
        # included in the fitted instance
        if not set(data.unique()).issubset(set(self.labels)):
            raise ValueError(
                "The data contains categories that the object hasn't seen",
                " in the fitting process.", 
                " Please check the data categories again.")

        return pd.Categorical(self._transform(data))
    
    def _transform():
        """
        _transform method is implemented in subclasses.

        transform method is responsible for general action 
            defined by the base class.
        _transform method is for specific procedure 
            conducted by each subclasses.
        """
        raise NotImplementedError("_transform method should be implemented " + \
                                  "in subclasses.")

    def inverse_transform(self, data: pd.Series) -> pd.Series | np.ndarray:
        """
        Base method of `inverse_transform`.

        Args:
            data (pd.Series): The data to be inverse transformed.

        Return:
            (pd.Series | np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        return self._inverse_transform(data.to_numpy())
    
    def _inverse_transform():
        """
        _inverse_transform method is implemented in subclasses.

        inverse_transform method is responsible for general action 
            defined by the base class.
        _inverse_transform method is for specific procedure 
            conducted by each subclasses.
        """
        raise NotImplementedError("_inverse_transform method should be " +\
                                  "implemented in subclasses.")


class EncoderUniform(Encoder):
    """
    Implement a uniform encoder.
    """

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

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        # Filter the counts > 0
        normalize_value_counts = data.value_counts(normalize=True)\
            .loc[lambda x: x > 0]
        # Get keys (original labels)
        self.labels = normalize_value_counts.index.get_level_values(
            0).to_list()
        # Get values (upper and lower bounds)
        self.upper_values = np.cumsum(normalize_value_counts.values)
        self.lower_values = np.roll(self.upper_values, 1)
        # To make sure the range of the data is in [0, 1]. 
        # That is, the range of an uniform dist.
        self.upper_values[-1] = 1.0
        self.lower_values[0] = 0.0

        self.cat_to_val = dict(zip(self.labels, list(
            zip(self.lower_values, self.upper_values))))

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a uniform distribution. 
            For example, a column with two categories (e.g., 'Male', 'Female')
                  can be mapped to [0.0, 0.5) and [0.5, 1], respectively.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        if isinstance(data.dtype, pd.api.types.CategoricalDtype):
            data_obj = data.astype(object)
        else:
            data_obj = data.copy()

        return data_obj.map(lambda x: self._rgenerator.\
                            uniform(self.cat_to_val[x][0], 
                                    self.cat_to_val[x][1], size=1)[0]).values

    def _inverse_transform(self, data: np.ndarray) -> pd.Series:
        """
        Inverse the transformed data to the categorical data.

        Args:
            data (np.ndarray): The categorical data needed to 
            be transformed inversely.

        Return:
            (pd.Series): The inverse transformed data.
        """

        # Check the range of the data is valid
        if data.max() > 1 or data.min() < 0:
            raise ValueError(
                "The range of the data is out of range.",
                " Please check the data again.")

        bins_val = np.append(self.lower_values, 1.0)

        return pd.cut(data, right=False, include_lowest=True, bins=bins_val, 
                      labels=self.labels, ordered=False)


class EncoderLabel(Encoder):
    """
    Implement a label encoder.
    """

    PROC_TYPE = ('encoder', 'discretizing')

    def __init__(self) -> None:
        super().__init__()
        self.model = LabelEncoder()

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        self.model.fit(data)

        # Get keys (original labels)
        self.labels = list(self.model.classes_)

        self.cat_to_val = dict(zip(self.labels, list(
            self.model.transform(self.model.classes_))))

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a series of integer labels.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        return self.model.transform(data)

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the categorical data.

        Args:
            data (np.ndarray): The categorical data needed to 
            be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """

        return self.model.inverse_transform(data)
    
class EncoderOneHot(Encoder):
    """
    Implement a one-hot encoder.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model = OneHotEncoder(sparse_output=False)

        # for the use in Mediator
        self._transform_temp: np.ndarray = None

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        self.model.fit(data.values.reshape(-1, 1))

        # Set original labels
        self.labels = self.model.categories_[0].tolist()

    def _transform(self, data: pd.Series) -> None:
        """
        Transform categorical data to a one-hot numeric array.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            None: The transformed data is stored in _transform_temp.
            data (pd.Series): Original data (dummy).
        """

        self._transform_temp = self.model.transform(data.values.reshape(-1, 1))

        return data

    def _inverse_transform(self, data: np.ndarray) -> None:
        """
        Inverse the transformed data to the categorical data.
        This is a dummy method, and it is implemented in MediatorEncoder.

        Args:
            data (np.ndarray): The categorical data needed to 
            be transformed inversely.

        Return:
            data (pd.Series): Original data (dummy).
        """

        return data
