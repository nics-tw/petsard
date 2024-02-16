from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

from PETsARD.processor.missing import MissingDrop
from PETsARD.processor.outlier import *


class Mediator:
    """
    Deal with the processors with the same type to 
    manage (column-wise) global behaviours including dropping the records.
    It is responsible for two actions:
        1. Gather all columns needed to process
        2. Coordinate and perform global behaviours
    """

    def __init__(self) -> None:
        self._process_col: list = []
        self._is_fitted: bool = False

    def fit(self, data: None) -> None:
        """
        Base method of `fit`.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        # in most cases, mediator doesn't need data to fit
        # just to keep the interface unified
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

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Base method of `transform`.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            (pd.DataFrame): The finished data.
        """
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if len(self._process_col) == 0:
            return data
        else:
            return self._transform(data)
        
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


class MediatorMissing(Mediator):
    """
    Deal with global behaviours in MissingHandler.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data 
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config['missing']

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        for col, obj in self._config.items():
            if type(obj) == MissingDrop:
                self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        if len(self._process_col) == 1:
            col_name: str = self._process_col[0]
            process_filter: np.ndarray = data[col_name].values

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            # restore the original data from the boolean data
            transformed[col_name] = self._config.get(col_name, None).\
                                            data_backup[~process_filter].values

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(
                axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed[col] = self._config.get(col, None).\
                                            data_backup[~process_filter].values

            return transformed


class MediatorOutlier(Mediator):
    """
    Deal with global behaviours in OutlierHandler.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data 
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config['outlier']
        self.model = None

        # indicator for using global outlier methods, 
        # such as Isolation Forest and Local Outlier Factor
        self._global_model_indicator: bool = False

        # if any column in the config sets outlier method 
        # as isolation forest or local outlier factor
        # it sets the overall transformation as that one
        for col, obj in self._config.items():
            if type(obj) == OutlierIsolationForest:
                self.model = IsolationForest()
                self._global_model_indicator = True
                break
            elif type(obj) == OutlierLOF:
                self.model = LocalOutlierFactor()
                self._global_model_indicator = True
                break
            else:
                pass

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        if self._global_model_indicator:
            # global transformation from sklearn only accepts numeric type data
            self._process_col = list(
                data.columns[data.apply(pd.api.types.is_numeric_dtype, axis=0)])

            if len(self._process_col) < 1:
                raise ValueError(
                    'There should be at least one numerical column \
                        to fit the model.')
        else:
            for col, obj in self._config.items():
                if type(obj) in [OutlierIQR, OutlierZScore]:
                    self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        if self._global_model_indicator:
            # the model may classify most data as outliers 
            # after transformation by other processors
            # so fit_predict will be used in _transform
            predict_result: np.ndarray = self.model.fit_predict(
                data[self._process_col])
            self.result: np.ndarray = predict_result
            process_filter: np.ndarray = predict_result == -1.0

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            return transformed
        elif len(self._process_col) == 1:
            col_name: str = self._process_col[0]
            process_filter: np.ndarray = data[col_name].values

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            # restore the original data from the boolean data
            transformed[col_name] = self._config.get(col_name, None).\
                                                data_backup[~process_filter]

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(
                axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed[col] = self._config.get(col, None).\
                                                data_backup[~process_filter]

            return transformed
