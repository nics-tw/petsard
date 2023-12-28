from torch import Value
from ..Processor.Missingist import Missingist_Drop
from ..Processor.Outlierist import *

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

class Mediator:
    """
    Deal with the processors with the same type to manage (column-wise) global behaviours including dropping the records.
    It is responsible for three actions:
        1. Gather all columns needed to process
        2. Coordinate and perform global behaviours
    """
    def __init__(self) -> None:
        self._process_col = []
        self._is_fitted = False

    def fit(self, data: None) -> None:
        """
        Base method of `fit`.

        Input:
            None, the config is read during initialisation.
            data: Redundant input.

        Output:
            None
        """
        # in most cases, mediator doesn't need data to fit
        # just to keep the interface unified
        self._fit(data)

        self._is_fitted = True

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Base method of `transform`.

        Input:
            data (pd.DataFrame): The in-processing data.

        Output:
            (pd.DataFrame): The finished data.
        """
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')
        
        if len(self._process_col) == 0:
            return data
        else:
            return self._transform(data)


class Mediator_Missingist(Mediator):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config['missingist']

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Input:
            None, the config is read during initialisation.
            data: Redundant input.

        Output:
            None
        """
        for col, obj in self._config.items():
            if type(obj) == Missingist_Drop:
                self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Input:
            data (pd.DataFrame): The in-processing data.

        Output:
            (pd.DataFrame): The finished data.
        """
        if len(self._process_col) == 1:
            col_name = self._process_col[0]
            process_filter = data[col_name].values

            transformed = data.loc[~process_filter, :].reset_index(drop=True)

            # restore the original data from the boolean data
            transformed.loc[:, col_name] = self._config.get(col_name, None).data_backup[~process_filter].values

            return transformed
        else:
            process_filter = data[self._process_col].any(axis=1).values

            transformed = data.loc[~process_filter, :].reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed.loc[:, col] = self._config.get(col, None).data_backup[~process_filter].values

            return transformed

class Mediator_Outlierist(Mediator):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config['outlierist']
        self.model = None

        # indicator for using global outlier methods, such as Isolation Forest and Local Outlier Factor
        self._global_model_indicator = False

        # if any column in the config sets outlierist method as isolation forest or local outlier factor
        # it sets the overall transformation as that one
        for col, obj in self._config.items():
            if type(obj) == Outlierist_IsolationForest:
                self.model = IsolationForest()
                self._global_model_indicator = True
                break
            elif type(obj) == Outlierist_LOF:
                self.model = LocalOutlierFactor()
                self._global_model_indicator = True
                break
            else:
                pass


    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Input:
            None, the config is read during initialisation.
            data: Redundant input.

        Output:
            None
        """
        if self._global_model_indicator:
            # global transformation from sklearn only accepts numeric type data
            self._process_col = list(data.columns[data.apply(pd.api.types.is_numeric_dtype, axis=0)])

            if len(self._process_col) < 1:
                raise ValueError('There should be at least one numerical column to fit the model.')
        else:
            for col, obj in self._config.items():
                if type(obj) in [Outlierist_IQR, Outlierist_ZScore]:
                    self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Input:
            data (pd.DataFrame): The in-processing data.

        Output:
            (pd.DataFrame): The finished data.
        """
        if self._global_model_indicator:
            # the model may classify most data as outliers after transformation by other processors
            # so fit_predict will be used in _transform
            predict_result = self.model.fit_predict(data[self._process_col])
            self.result = predict_result
            process_filter = predict_result == -1.0

            transformed = data.loc[~process_filter, :].reset_index(drop=True)

            return transformed
        elif len(self._process_col) == 1:
            col_name = self._process_col[0]
            process_filter = data[col_name].values

            transformed = data.loc[~process_filter, :].reset_index(drop=True)

            # restore the original data from the boolean data
            transformed.loc[:, col_name] = self._config.get(col_name, None).data_backup[~process_filter]

            return transformed
        else:
            process_filter = data[self._process_col].any(axis=1).values

            transformed = data.loc[~process_filter, :].reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed.loc[:, col] = self._config.get(col, None).data_backup[~process_filter]

            return transformed